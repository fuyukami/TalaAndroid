// Luật tính tiền. Thuần Dart, không dính giao diện, để viết test.
//
// Mỗi hàm build* chỉ đọc trạng thái và trả về một sự kiện (hoặc lỗi);
// việc áp dụng sự kiện do [applyEvent] làm.

import 'models.dart';

class RuleResult {
  final GameEvent? event;
  final String? error;
  const RuleResult.ok(GameEvent this.event) : error = null;
  const RuleResult.fail(String this.error) : event = null;
  bool get ok => event != null;
}

bool _isActive(GameState s, String? id) => id != null && s.active.any((p) => p.id == id);

// ---------------------------------------------------------------------------
// Ăn cây
// ---------------------------------------------------------------------------

/// Số lần [loserId] đã bị ăn cây trong ván hiện tại.
int anCayCount(GameState s, String loserId) =>
    s.current.where((e) => e.type == EventType.anCay && e.loserId == loserId).length;

/// Người đã ăn cây của [loserId] trong ván này (nếu có).
String? anCayWinnerOf(GameState s, String loserId) {
  for (final e in s.current) {
    if (e.type == EventType.anCay && e.loserId == loserId) return e.winnerId;
  }
  return null;
}

/// Những người được phép ăn cây của [loserId].
/// Đã có người ăn thì chỉ người đó ăn tiếp; chưa có thì là những người
/// chưa ăn cây của ai khác.
List<Player> anCayWinnersFor(GameState s, String loserId) {
  final existing = anCayWinnerOf(s, loserId);
  if (existing != null) return s.active.where((p) => p.id == existing).toList();
  final used = s.current
      .where((e) => e.type == EventType.anCay && e.loserId != loserId)
      .map((e) => e.winnerId)
      .toSet();
  return s.active.where((p) => p.id != loserId && !used.contains(p.id)).toList();
}

RuleResult buildAnCay(GameState s, String loserId, String winnerId, {DateTime? now}) {
  if (!_isActive(s, loserId) || !_isActive(s, winnerId) || loserId == winnerId) {
    return const RuleResult.fail('Người chơi không hợp lệ.');
  }
  final count = anCayCount(s, loserId);
  if (count >= 3) {
    return RuleResult.fail('${s.nameOf(loserId)} đã bị ăn tối đa 3 cây.');
  }
  if (!anCayWinnersFor(s, loserId).any((p) => p.id == winnerId)) {
    return RuleResult.fail('${s.nameOf(winnerId)} không thể ăn cây của ${s.nameOf(loserId)}.');
  }
  final lan = count + 1;
  final amt = s.settings.bet * s.settings.anCay[lan - 1];
  return RuleResult.ok(GameEvent(
    type: EventType.anCay,
    time: now ?? DateTime.now(),
    loserId: loserId,
    winnerId: winnerId,
    lan: lan,
    deltas: {loserId: -amt, winnerId: amt},
  ));
}

// ---------------------------------------------------------------------------
// Ăn chốt
// ---------------------------------------------------------------------------

RuleResult buildAnChot(GameState s, String loserId, String winnerId, {DateTime? now}) {
  if (!_isActive(s, loserId) || !_isActive(s, winnerId) || loserId == winnerId) {
    return const RuleResult.fail('Người chơi không hợp lệ.');
  }
  final amt = s.settings.bet * s.settings.anChot;
  return RuleResult.ok(GameEvent(
    type: EventType.anChot,
    time: now ?? DateTime.now(),
    loserId: loserId,
    winnerId: winnerId,
    deltas: {loserId: -amt, winnerId: amt},
  ));
}

// ---------------------------------------------------------------------------
// Nộp gà
// ---------------------------------------------------------------------------

int nopGaCount(GameState s, String playerId) =>
    s.current.where((e) => e.type == EventType.nopGa && e.loserId == playerId).length;

RuleResult buildNopGa(GameState s, String playerId, {DateTime? now}) {
  if (!_isActive(s, playerId)) return const RuleResult.fail('Người chơi không hợp lệ.');
  final count = nopGaCount(s, playerId);
  if (count >= 3) {
    return RuleResult.fail('${s.nameOf(playerId)} đã nộp gà tối đa 3 lần.');
  }
  final lan = count + 1;
  final amt = s.settings.bet * s.settings.nopGa[lan - 1];
  return RuleResult.ok(GameEvent(
    type: EventType.nopGa,
    time: now ?? DateTime.now(),
    loserId: playerId,
    lan: lan,
    deltas: {playerId: -amt},
    potDelta: amt,
  ));
}

// ---------------------------------------------------------------------------
// Ù
// ---------------------------------------------------------------------------

/// [denId] = null nghĩa là không ai đền: mỗi người còn lại trả cược × hệ số Ù.
/// Có người đền: người đó trả thay cả làng.
RuleResult buildU(GameState s, String uId, String? denId, {DateTime? now}) {
  if (!_isActive(s, uId)) return const RuleResult.fail('Người chơi không hợp lệ.');
  if (denId != null && (!_isActive(s, denId) || denId == uId)) {
    return const RuleResult.fail('Người đền không hợp lệ.');
  }
  final others = s.active.where((p) => p.id != uId).toList();
  final tien = s.settings.bet * s.settings.uMoiNguoi;
  final tong = tien * others.length;
  final deltas = <String, int>{};
  if (denId == null) {
    for (final p in others) {
      deltas[p.id] = -tien;
    }
  } else {
    deltas[denId] = -tong;
  }
  deltas[uId] = tong + s.pot;
  return RuleResult.ok(GameEvent(
    type: EventType.u,
    time: now ?? DateTime.now(),
    winnerId: uId,
    loserId: denId,
    deltas: deltas,
    potDelta: -s.pot,
  ));
}

// ---------------------------------------------------------------------------
// Xếp hạng
// ---------------------------------------------------------------------------

const List<Hang> kThuTuThua = [Hang.nhi, Hang.ba, Hang.bet];

/// Kiểm tra bảng xếp hạng. Trả về null nếu hợp lệ, ngược lại là thông báo lỗi.
/// Luật: đúng một người Nhất; những người không Móm lần lượt là Nhì, Ba, Bét
/// (k người thì dùng k hạng đầu, không trùng).
String? validateXepHang(GameState s, Map<String, Hang> hang) {
  final ids = s.active.map((p) => p.id).toList();
  for (final id in ids) {
    if (!hang.containsKey(id)) return 'Chưa chọn hạng cho ${s.nameOf(id)}.';
  }
  final nhat = ids.where((id) => hang[id] == Hang.nhat).length;
  if (nhat != 1) return 'Phải có đúng một người Nhất.';
  final thuong = ids.where((id) => hang[id] != Hang.nhat && hang[id] != Hang.mom).toList();
  final can = kThuTuThua.take(thuong.length).toSet();
  final co = thuong.map((id) => hang[id]).toSet();
  if (co.length != thuong.length || !co.containsAll(can) || !can.containsAll(co)) {
    final ten = can.map((h) => kTenHang[h]).join(', ');
    return thuong.isEmpty
        ? null
        : 'Những người không móm phải lần lượt là: $ten (mỗi hạng một người).';
  }
  return null;
}

RuleResult buildXepHang(GameState s, Map<String, Hang> hang, {DateTime? now}) {
  final err = validateXepHang(s, hang);
  if (err != null) return RuleResult.fail(err);
  final ids = s.active.map((p) => p.id).toList();
  final nhatId = ids.firstWhere((id) => hang[id] == Hang.nhat);
  final deltas = <String, int>{};
  var tong = 0;
  for (final id in ids) {
    final h = hang[id]!;
    if (h == Hang.nhat) continue;
    final heSo = h == Hang.mom ? s.settings.mom : s.settings.xepHang[kThuTuThua.indexOf(h)];
    final amt = s.settings.bet * heSo;
    deltas[id] = -amt;
    tong += amt;
  }
  deltas[nhatId] = tong;
  return RuleResult.ok(GameEvent(
    type: EventType.xepHang,
    time: now ?? DateTime.now(),
    winnerId: nhatId,
    deltas: deltas,
    hang: {for (final id in ids) id: hang[id]!},
  ));
}

// ---------------------------------------------------------------------------
// Áp dụng sự kiện
// ---------------------------------------------------------------------------

bool endsRound(EventType t) => t == EventType.u || t == EventType.xepHang;

/// Áp dụng [e] vào [s]. Nếu là Ù hoặc xếp hạng thì đóng ván, đưa vào lịch sử.
void applyEvent(GameState s, GameEvent e) {
  e.deltas.forEach((id, d) => s.byId(id).money += d);
  s.pot += e.potDelta;
  s.current.add(e);
  if (endsRound(e.type)) {
    final ids = s.active.map((p) => p.id).toList();
    final deltas = {for (final id in ids) id: 0};
    for (final ev in s.current) {
      ev.deltas.forEach((id, d) => deltas[id] = (deltas[id] ?? 0) + d);
    }
    s.history.insert(
      0,
      Round(
        number: s.roundNumber,
        endedAt: e.time,
        events: List.of(s.current),
        deltas: deltas,
        totalsAfter: {for (final id in ids) id: s.byId(id).money},
        playerIds: ids,
      ),
    );
    s.current = [];
  }
}

/// Tổng +/- từng người trong ván đang chơi.
Map<String, int> currentDeltas(GameState s) {
  final m = {for (final p in s.active) p.id: 0};
  for (final e in s.current) {
    e.deltas.forEach((id, d) => m[id] = (m[id] ?? 0) + d);
  }
  return m;
}

// ---------------------------------------------------------------------------
// Mô tả bằng chữ
// ---------------------------------------------------------------------------

String fmtK(int v, {bool sign = false}) {
  final abs = v.abs().toString().replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]}.');
  if (!sign) return '${v < 0 ? '−' : ''}${abs}k';
  if (v > 0) return '+${abs}k';
  if (v < 0) return '−${abs}k';
  return '0k';
}

String describeEvent(GameState s, GameEvent e) {
  final l = s.nameOf(e.loserId);
  final w = s.nameOf(e.winnerId);
  switch (e.type) {
    case EventType.anCay:
      return '$w ăn cây ${e.lan} của $l';
    case EventType.anChot:
      return '$w ăn chốt của $l';
    case EventType.nopGa:
      return '$l nộp gà lần ${e.lan}';
    case EventType.u:
      return e.loserId == null ? '$w Ù, không ai đền' : '$w Ù, $l đền làng';
    case EventType.xepHang:
      return 'Xếp hạng: $w Nhất';
  }
}

/// Số tiền chính của sự kiện, để hiện bên phải dòng diễn biến.
int eventAmount(GameEvent e) {
  switch (e.type) {
    case EventType.nopGa:
      return e.potDelta;
    case EventType.u:
    case EventType.xepHang:
      return e.deltas[e.winnerId] ?? 0;
    default:
      return e.deltas[e.winnerId] ?? 0;
  }
}

String roundTitle(GameState s, Round r) {
  final e = r.last;
  if (e.type == EventType.u) return 'Ván ${r.number} · ${s.nameOf(e.winnerId)} Ù';
  return 'Ván ${r.number} · Xếp hạng';
}
