import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// Lưu dữ liệu app vào một file JSON trong thư mục riêng của app.
/// Ghi ra file tạm rồi đổi tên, để mất điện giữa chừng không làm hỏng file.
class Storage {
  static const int schemaVersion = 1;
  final Future<Directory> Function() _dir;

  Storage({Future<Directory> Function()? dir})
      : _dir = dir ?? getApplicationSupportDirectory;

  Future<File> _file() async => File('${(await _dir()).path}/tala_data.json');

  Future<Map<String, dynamic>?> load() async {
    final f = await _file();
    if (!await f.exists()) return null;
    try {
      final j = jsonDecode(await f.readAsString());
      if (j is Map<String, dynamic>) return j;
      throw const FormatException('not an object');
    } catch (_) {
      // File hỏng: giữ lại bản lỗi để không mất hẳn, rồi khởi tạo mới.
      try {
        await f.copy('${f.path}.bak');
      } catch (_) {}
      return null;
    }
  }

  Future<void>? _pending;
  Map<String, dynamic>? _queued;

  /// Ghi tuần tự: nếu đang ghi dở thì chỉ giữ bản mới nhất để ghi tiếp.
  Future<void> save(Map<String, dynamic> data) {
    _queued = {'version': schemaVersion, ...data};
    return _pending ??= _drain();
  }

  Future<void> _drain() async {
    try {
      while (_queued != null) {
        final d = _queued!;
        _queued = null;
        final f = await _file();
        final tmp = File('${f.path}.tmp');
        await tmp.writeAsString(jsonEncode(d), flush: true);
        await tmp.rename(f.path);
      }
    } finally {
      _pending = null;
    }
  }
}
