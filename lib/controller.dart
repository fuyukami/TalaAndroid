import 'package:flutter/foundation.dart';

import 'models.dart';
import 'rules.dart';
import 'storage.dart';

class UndoEntry {
  final String label;
  final Map<String, dynamic> snapshot;
  UndoEntry(this.label, this.snapshot);

  Map<String, dynamic> toJson() => {'label': label, 'snapshot': snapshot};
  factory UndoEntry.fromJson(Map<String, dynamic> j) =>
      UndoEntry(j['label'] as String, Map<String, dynamic>.from(j['snapshot'] as Map));
}

/// Giữ trạng thái app, ngăn hoàn tác, và lưu xuống file sau mỗi thay đổi.
class GameController extends ChangeNotifier {
  static const int maxUndo = 30;

  GameState state;
  final List<UndoEntry> _undo;
  final Storage? storage;

  GameController({GameState? state, List<UndoEntry>? undo, this.storage})
      : state = state ?? GameState.initial(),
        _undo = undo ?? [];

  static Future<GameController> load(Storage storage) async {
    final j = await storage.load();
    if (j == null) return GameController(storage: storage);
    try {
      final st = GameState.fromJson(Map<String, dynamic>.from(j['state'] as Map));
      final undo = ((j['undo'] as List?) ?? [])
          .map((e) => UndoEntry.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList();
      return GameController(state: st, undo: undo, storage: storage);
    } catch (_) {
      return GameController(storage: storage);
    }
  }

  // ----- đọc -----
  List<Player> get active => state.active;
  String name(String? id) => state.nameOf(id);
  bool get canUndo => _undo.isNotEmpty;
  String? get undoLabel => _undo.isEmpty ? null : _undo.last.label;

  // ----- lưu -----
  Future<void> save() async {
    await storage?.save({
      'state': state.toJson(),
      'undo': _undo.map((u) => u.toJson()).toList(),
    });
  }

  void _push(String label) {
    _undo.add(UndoEntry(label, state.toJson()));
    if (_undo.length > maxUndo) _undo.removeAt(0);
  }

  void _commit() {
    notifyListeners();
    save();
  }

  /// Áp dụng kết quả của một hàm build* trong rules.dart.
  /// Trả về lỗi (nếu có) để giao diện hiện thông báo.
  String? apply(RuleResult r) {
    if (!r.ok) return r.error;
    final e = r.event!;
    _push('${describeEvent(state, e)} (${fmtK(eventAmount(e), sign: e.type != EventType.nopGa)})');
    applyEvent(state, e);
    _commit();
    return null;
  }

  String? undo() {
    if (_undo.isEmpty) return null;
    final u = _undo.removeLast();
    state = GameState.fromJson(u.snapshot);
    _commit();
    return u.label;
  }

  void reset() {
    _push('Reset toàn bộ');
    for (final p in state.players) {
      p.money = 0;
    }
    state.pot = 0;
    state.current = [];
    state.history = [];
    _commit();
  }

  /// Đổi tên. Trả về lỗi nếu tên rỗng hoặc trùng.
  String? rename(String id, String newName) {
    final n = newName.trim();
    if (n.isEmpty) return 'Tên không được để trống.';
    if (n.length > 20) return 'Tên tối đa 20 ký tự.';
    if (state.active.any((p) => p.id != id && p.name.toLowerCase() == n.toLowerCase())) {
      return 'Đã có người tên "$n".';
    }
    final p = state.byId(id);
    if (p.name == n) return null;
    _push('Đổi tên ${p.name} thành $n');
    p.name = n;
    _commit();
    return null;
  }

  /// Lưu cài đặt và tên người chơi cùng lúc. Trả về lỗi nếu có.
  String? updateSettings(Settings s, Map<String, String> names) {
    if (s.bet <= 0) return 'Mức cược phải là số dương.';
    final all = [s.uMoiNguoi, s.anChot, s.mom, ...s.anCay, ...s.nopGa, ...s.xepHang];
    if (all.any((v) => v <= 0 || v > 1000)) return 'Hệ số phải từ 1 đến 1000.';
    if (s.playerCount < kMinPlayers || s.playerCount > kMaxPlayers) {
      return 'Số người chơi phải từ $kMinPlayers đến $kMaxPlayers.';
    }
    if (s.playerCount != state.settings.playerCount && state.current.isNotEmpty) {
      return 'Ván đang chơi dở. Hãy kết thúc ván (Ù hoặc xếp hạng) rồi mới đổi số người chơi.';
    }
    final cleaned = <String, String>{};
    for (final p in state.players) {
      final n = (names[p.id] ?? p.name).trim();
      if (n.isEmpty) return 'Tên không được để trống.';
      if (n.length > 20) return 'Tên tối đa 20 ký tự.';
      cleaned[p.id] = n;
    }
    final activeNames = state.players
        .take(s.playerCount)
        .map((p) => cleaned[p.id]!.toLowerCase())
        .toList();
    if (activeNames.toSet().length != activeNames.length) {
      return 'Không được đặt hai người trùng tên.';
    }
    _push('Đổi cài đặt');
    state.settings = s.copy();
    for (final p in state.players) {
      p.name = cleaned[p.id]!;
    }
    _commit();
    return null;
  }
}
