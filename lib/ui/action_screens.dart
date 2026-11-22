import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import '../main.dart';
import '../models.dart';
import '../rules.dart';
import 'widgets.dart';

// Mỗi luồng là một màn duy nhất, có nút XÁC NHẬN. Vuốt quay lại / Huỷ chỉ
// có nghĩa là huỷ: tiền chỉ thay đổi khi bấm Xác nhận.

/// Khung chung cho các màn thao tác.
class _ActionFrame extends StatelessWidget {
  final String title;
  final List<Widget> children;
  final VoidCallback? onConfirm;
  final String confirmLabel;

  const _ActionFrame({
    required this.title,
    required this.children,
    required this.onConfirm,
    this.confirmLabel = 'XÁC NHẬN',
  });

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return ScreenFrame(
      title: title,
      bottom: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Expanded(
                  child: GlassButton(
                      label: 'Huỷ', height: 58, onPressed: () => Navigator.of(context).pop())),
              const SizedBox(width: 12),
              Expanded(
                child: Raised3DButton(
                    label: confirmLabel, colors: BtnColors.green, onPressed: onConfirm, height: 58),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text('Vuốt quay lại = huỷ, chưa có tiền nào bị cộng trừ',
              style: TextStyle(fontSize: 12, color: p.onFeltSub)),
        ],
      ),
      children: children,
    );
  }
}

/// Áp dụng thao tác và đóng màn. Chỉ báo khi có lỗi. Trả về true nếu thành công.
bool _commit(BuildContext context, RuleResult r) {
  final c = Ctl.read(context);
  final err = c.apply(r);
  if (err != null) {
    showMsg(context, err, error: true);
    return false;
  }
  HapticFeedback.mediumImpact();
  Navigator.of(context).pop();
  return true;
}

class _PreviewLine extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;
  final bool big;
  const _PreviewLine(this.label, this.value, {this.color, this.big = false});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    final style = TextStyle(fontSize: big ? 18 : 15, fontWeight: big ? FontWeight.w800 : FontWeight.w500);
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        children: [
          Expanded(child: Text(label, style: style.copyWith(color: p.onFelt))),
          Text(value, style: style.copyWith(fontWeight: FontWeight.w700, color: color ?? p.onFelt)),
        ],
      ),
    );
  }
}

const _plus = Color(0xFF8EE0B2);
const _minus = Color(0xFFFFB4AB);
const _gold = Color(0xFFF3D27A);

Widget _previewDeltas(GameState s, GameEvent e, {String? note}) {
  final ids = e.deltas.keys.toList()
    ..sort((a, b) => (e.deltas[a]!).compareTo(e.deltas[b]!));
  return FeltPanel(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SectionLabel('Xem trước kết quả', onFelt: true),
        if (note != null)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(note, style: const TextStyle(fontSize: 13, color: Color(0xFFB9DCCB))),
          ),
        for (final id in ids)
          _PreviewLine(s.nameOf(id), fmtK(e.deltas[id]!, sign: true),
              color: e.deltas[id]! < 0 ? _minus : _plus),
        if (e.potDelta != 0)
          _PreviewLine('Quỹ gà', fmtK(e.potDelta, sign: true), color: _gold),
      ],
    ),
  );
}

// ---------------------------------------------------------------------------
// Ăn cây
// ---------------------------------------------------------------------------

class AnCayScreen extends StatefulWidget {
  const AnCayScreen({super.key});
  @override
  State<AnCayScreen> createState() => _AnCayScreenState();
}

class _AnCayScreenState extends State<AnCayScreen> {
  String? loser, winner;

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final winners = loser == null ? <Player>[] : anCayWinnersFor(s, loser!);
    if (winners.length == 1) winner = winners.first.id;
    if (winner != null && !winners.any((p) => p.id == winner)) winner = null;
    final r = (loser != null && winner != null) ? buildAnCay(s, loser!, winner!) : null;

    return _ActionFrame(
      title: 'Ăn cây',
      onConfirm: r?.ok == true
          ? () => _commit(context, r!)
          : null,
      children: [
        Panel(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const SectionLabel('1 · Ai bị ăn cây?'),
            const SizedBox(height: 12),
            TileGrid(children: [
              for (final pl in s.active)
                Builder(builder: (_) {
                  final n = anCayCount(s, pl.id);
                  final none = anCayWinnersFor(s, pl.id).isEmpty;
                  final disabled = n >= 3 || none;
                  return ChoiceTile(
                    label: pl.name,
                    hint: n >= 3
                        ? 'đã bị ăn 3 cây'
                        : none
                            ? 'không còn ai ăn được'
                            : (n > 0 ? 'đã bị ăn $n cây' : null),
                    selected: loser == pl.id,
                    selectedColors: BtnColors.green,
                    onTap: disabled ? null : () => setState(() {
                          loser = pl.id;
                          winner = null;
                        }),
                  );
                }),
            ]),
          ]),
        ),
        if (loser != null)
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              SectionLabel('2 · Ai ăn cây của ${s.nameOf(loser)}?'),
              const SizedBox(height: 12),
              TileGrid(children: [
                for (final pl in winners)
                  ChoiceTile(
                    label: pl.name,
                    hint: anCayWinnerOf(s, loser!) == pl.id ? 'đã ăn trước đó' : null,
                    selected: winner == pl.id,
                    selectedColors: BtnColors.green,
                    onTap: () => setState(() => winner = pl.id),
                  ),
              ]),
            ]),
          ),
        if (r?.ok == true)
          _previewDeltas(s, r!.event!,
              note: 'Cây lần ${r.event!.lan}: cược ${s.settings.bet}k × ${s.settings.anCay[r.event!.lan - 1]}'),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Ăn chốt
// ---------------------------------------------------------------------------

class AnChotScreen extends StatefulWidget {
  const AnChotScreen({super.key});
  @override
  State<AnChotScreen> createState() => _AnChotScreenState();
}

class _AnChotScreenState extends State<AnChotScreen> {
  String? loser, winner;

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    if (winner == loser) winner = null;
    final r = (loser != null && winner != null) ? buildAnChot(s, loser!, winner!) : null;
    return _ActionFrame(
      title: 'Ăn chốt',
      onConfirm: r?.ok == true
          ? () => _commit(context, r!)
          : null,
      children: [
        Panel(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const SectionLabel('1 · Ai bị ăn chốt?'),
            const SizedBox(height: 12),
            TileGrid(children: [
              for (final pl in s.active)
                ChoiceTile(
                  label: pl.name,
                  selected: loser == pl.id,
                  selectedColors: BtnColors.pink,
                  onTap: () => setState(() => loser = pl.id),
                ),
            ]),
          ]),
        ),
        if (loser != null)
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              SectionLabel('2 · Ai ăn chốt của ${s.nameOf(loser)}?'),
              const SizedBox(height: 12),
              TileGrid(children: [
                for (final pl in s.active.where((p) => p.id != loser))
                  ChoiceTile(
                    label: pl.name,
                    selected: winner == pl.id,
                    selectedColors: BtnColors.pink,
                    onTap: () => setState(() => winner = pl.id),
                  ),
              ]),
            ]),
          ),
        if (r?.ok == true)
          _previewDeltas(s, r!.event!, note: 'Chốt: cược ${s.settings.bet}k × ${s.settings.anChot}'),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Nộp gà
// ---------------------------------------------------------------------------

class NopGaScreen extends StatefulWidget {
  const NopGaScreen({super.key});
  @override
  State<NopGaScreen> createState() => _NopGaScreenState();
}

class _NopGaScreenState extends State<NopGaScreen> {
  String? who;

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final r = who != null ? buildNopGa(s, who!) : null;
    return _ActionFrame(
      title: 'Nộp gà',
      onConfirm: r?.ok == true
          ? () => _commit(context, r!)
          : null,
      children: [
        Panel(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const SectionLabel('Ai nộp gà?'),
            const SizedBox(height: 12),
            TileGrid(children: [
              for (final pl in s.active)
                Builder(builder: (_) {
                  final n = nopGaCount(s, pl.id);
                  return ChoiceTile(
                    label: pl.name,
                    hint: n >= 3 ? 'đã nộp 3 lần' : (n > 0 ? 'đã nộp $n lần' : null),
                    selected: who == pl.id,
                    selectedColors: BtnColors.amber,
                    onTap: n >= 3 ? null : () => setState(() => who = pl.id),
                  );
                }),
            ]),
          ]),
        ),
        if (r?.ok == true)
          FeltPanel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Xem trước kết quả', onFelt: true),
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(
                    'Lần ${r!.event!.lan}: cược ${s.settings.bet}k × ${s.settings.nopGa[r.event!.lan - 1]}',
                    style: const TextStyle(fontSize: 13, color: Color(0xFFB9DCCB))),
              ),
              _PreviewLine(s.nameOf(who), fmtK(-r.event!.potDelta, sign: true), color: _minus),
              _PreviewLine('Quỹ gà sau khi nộp', fmtK(s.pot + r.event!.potDelta), color: _gold, big: true),
            ]),
          ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Ù
// ---------------------------------------------------------------------------

class UScreen extends StatefulWidget {
  const UScreen({super.key});
  @override
  State<UScreen> createState() => _UScreenState();
}

class _UScreenState extends State<UScreen> {
  String? u;
  bool denChosen = false;
  String? den; // null + denChosen = không ai đền

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    if (den != null && den == u) {
      den = null;
      denChosen = false;
    }
    final r = (u != null && denChosen) ? buildU(s, u!, den) : null;
    final others = s.active.where((p) => p.id != u).toList();
    final tien = s.settings.bet * s.settings.uMoiNguoi;

    return _ActionFrame(
      title: 'Xử lý Ù',
      onConfirm: r?.ok == true
          ? () {
              final nav = Navigator.of(context);
              final amount = r!.event!.deltas[u]!;
              final name = s.nameOf(u);
              final id = u!;
              if (_commit(context, r)) {
                nav.push(CelebrationRoute(playerId: id, name: name, amount: amount));
              }
            }
          : null,
      children: [
        Panel(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const SectionLabel('1 · Ai Ù?'),
            const SizedBox(height: 12),
            TileGrid(children: [
              for (final pl in s.active)
                ChoiceTile(
                  label: pl.name,
                  selected: u == pl.id,
                  selectedColors: BtnColors.red,
                  onTap: () => setState(() => u = pl.id),
                ),
            ]),
          ]),
        ),
        if (u != null)
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('2 · Có ai đền làng không?'),
              const SizedBox(height: 12),
              ChoiceTile(
                label: 'Không ai đền',
                selected: denChosen && den == null,
                onTap: () => setState(() {
                  denChosen = true;
                  den = null;
                }),
              ),
              const SizedBox(height: 10),
              TileGrid(columns: others.length >= 3 ? 3 : others.length.clamp(1, 3), children: [
                for (final pl in others)
                  ChoiceTile(
                    label: pl.name,
                    hint: 'đền',
                    selected: den == pl.id,
                    onTap: () => setState(() {
                      denChosen = true;
                      den = pl.id;
                    }),
                  ),
              ]),
            ]),
          ),
        if (r?.ok == true)
          FeltPanel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Xem trước kết quả', onFelt: true),
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text('Mỗi người trả: cược ${s.settings.bet}k × ${s.settings.uMoiNguoi} = ${fmtK(tien)}',
                    style: const TextStyle(fontSize: 13, color: Color(0xFFB9DCCB))),
              ),
              if (den == null)
                for (final pl in others) _PreviewLine(pl.name, fmtK(-tien, sign: true), color: _minus)
              else
                _PreviewLine('${s.nameOf(den)} đền thay ${others.length} người',
                    fmtK(-tien * others.length, sign: true),
                    color: _minus),
              const Divider(color: Color(0x26FFFFFF), height: 20),
              _PreviewLine('${s.nameOf(u)} Ù (${others.length} × ${fmtK(tien)})',
                  fmtK(tien * others.length, sign: true),
                  color: _plus),
              if (s.pot > 0) _PreviewLine('Ăn quỹ gà', fmtK(s.pot, sign: true), color: _gold),
              _PreviewLine('${s.nameOf(u)} nhận', fmtK(r!.event!.deltas[u]!, sign: true),
                  color: _plus, big: true),
              const SizedBox(height: 6),
              const Text('Xác nhận sẽ kết thúc ván và lưu vào lịch sử.',
                  style: TextStyle(fontSize: 12, color: Color(0xFFB9DCCB))),
            ]),
          ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Xếp hạng
// ---------------------------------------------------------------------------

class XepHangScreen extends StatefulWidget {
  const XepHangScreen({super.key});
  @override
  State<XepHangScreen> createState() => _XepHangScreenState();
}

class _XepHangScreenState extends State<XepHangScreen> {
  final Map<String, Hang> hang = {};

  void _pick(GameState s, String id, Hang h) {
    setState(() {
      if (hang[id] == h) {
        hang.remove(id);
        return;
      }
      // Hạng Nhất / Nhì / Ba / Bét mỗi hạng chỉ một người.
      if (h != Hang.mom) hang.removeWhere((k, v) => v == h && k != id);
      hang[id] = h;
      // Còn đúng một người chưa chọn và chỉ còn một hạng hợp lệ: tự điền.
      final ids = s.active.map((p) => p.id).toList();
      final missing = ids.where((x) => !hang.containsKey(x)).toList();
      if (missing.length == 1 && hang.values.contains(Hang.nhat)) {
        final thuong = hang.values.where((v) => v != Hang.nhat && v != Hang.mom).length;
        if (thuong < ids.length - 1 && thuong < kThuTuThua.length) {
          final next = kThuTuThua[thuong];
          if (!hang.values.contains(next)) hang[missing.first] = next;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final p = Pal.of(context);
    final n = s.active.length;
    final options = [Hang.nhat, ...kThuTuThua.take(n - 1), Hang.mom];
    final err = validateXepHang(s, hang);
    final r = err == null ? buildXepHang(s, hang) : null;
    final deltaVan = currentDeltas(s);

    return _ActionFrame(
      title: 'Xếp hạng ván',
      confirmLabel: 'KẾT THÚC VÁN',
      onConfirm: r?.ok == true
          ? () => _commit(context, r!)
          : null,
      children: [
        Text('Chọn hạng cho từng người. Người không móm lần lượt là '
            '${kThuTuThua.take(n - 1).map((h) => kTenHang[h]).join(', ')}.',
            style: TextStyle(color: p.onFeltSub, fontSize: 14)),
        for (final pl in s.active)
          Panel(
            padding: const EdgeInsets.all(14),
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              Row(children: [
                Avatar(id: pl.id, name: pl.name, size: 34),
                const SizedBox(width: 10),
                Expanded(
                    child: Text(pl.name,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700))),
              ]),
              const SizedBox(height: 10),
              TileGrid(columns: options.length, gap: 6, children: [
                for (final h in options)
                  ChoiceTile(
                    label: kTenHang[h]!,
                    selected: hang[pl.id] == h,
                    showCheck: false,
                    selectedColors: h == Hang.nhat
                        ? BtnColors.blue
                        : h == Hang.mom
                            ? BtnColors.red
                            : BtnColors.amber,
                    onTap: () => _pick(s, pl.id, h),
                  ),
              ]),
            ]),
          ),
        if (r?.ok == true)
          FeltPanel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Xem trước kết quả', onFelt: true),
              for (final pl in s.active)
                _PreviewLine(
                  '${pl.name} (${kTenHang[hang[pl.id]]})',
                  fmtK(r!.event!.deltas[pl.id] ?? 0, sign: true),
                  color: (r.event!.deltas[pl.id] ?? 0) < 0 ? _minus : _plus,
                ),
              if (s.current.isNotEmpty) ...[
                const Divider(color: Color(0x26FFFFFF), height: 20),
                const Text('Tổng cả ván (gồm ăn cây, chốt, gà):',
                    style: TextStyle(fontSize: 13, color: Color(0xFFB9DCCB))),
                for (final pl in s.active)
                  _PreviewLine(
                    pl.name,
                    fmtK((deltaVan[pl.id] ?? 0) + (r!.event!.deltas[pl.id] ?? 0), sign: true),
                  ),
              ],
            ]),
          )
        else if (hang.isNotEmpty && err != null)
          FeltPanel(child: Text(err, style: const TextStyle(color: _gold, fontSize: 14))),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Màn mừng Ù: thẻ lật 3D + pháo hoa giấy
// ---------------------------------------------------------------------------

class CelebrationRoute extends PageRouteBuilder<void> {
  CelebrationRoute({required String playerId, required String name, required int amount})
      : super(
          opaque: false,
          barrierDismissible: true,
          barrierColor: const Color(0xB3000000),
          transitionDuration: const Duration(milliseconds: 200),
          pageBuilder: (_, _, _) =>
              _Celebration(playerId: playerId, name: name, amount: amount),
        );
}

class _Celebration extends StatefulWidget {
  final String playerId;
  final String name;
  final int amount;
  const _Celebration({required this.playerId, required this.name, required this.amount});

  @override
  State<_Celebration> createState() => _CelebrationState();
}

class _CelebrationState extends State<_Celebration> with TickerProviderStateMixin {
  late final AnimationController flip =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..forward();
  late final AnimationController fall =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 2800))..forward();
  final bits = ConfettiPainter.make(90, DateTime.now().millisecond);

  @override
  void initState() {
    super.initState();
    HapticFeedback.heavyImpact();
    Future.delayed(const Duration(milliseconds: 3600), () {
      if (mounted && ModalRoute.of(context)?.isCurrent == true) Navigator.of(context).pop();
    });
  }

  @override
  void dispose() {
    flip.dispose();
    fall.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () => Navigator.of(context).pop(),
      child: Stack(
        children: [
          Positioned.fill(
            child: AnimatedBuilder(
              animation: fall,
              builder: (_, _) => CustomPaint(painter: ConfettiPainter(fall.value, bits)),
            ),
          ),
          Center(
            child: AnimatedBuilder(
              animation: flip,
              builder: (_, _) {
                final t = Curves.easeOutBack.transform(flip.value);
                final angle = (1 - t) * math.pi;
                final showFront = angle < math.pi / 2;
                final m = Matrix4.identity()
                  ..setEntry(3, 2, 0.0015)
                  ..rotateY(angle);
                return Transform(
                  transform: m,
                  alignment: Alignment.center,
                  child: showFront
                      ? _front()
                      : Transform(
                          transform: Matrix4.rotationY(math.pi),
                          alignment: Alignment.center,
                          child: _back()),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _cardShell(Widget child, {Gradient? gradient, Color? color}) => Container(
        width: 240,
        height: 330,
        decoration: BoxDecoration(
          color: color,
          gradient: gradient,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFFF2C24E), width: 3),
          boxShadow: const [
            BoxShadow(color: Color(0x80000000), offset: Offset(0, 20), blurRadius: 40),
          ],
        ),
        child: child,
      );

  Widget _back() => _cardShell(
        const Center(
          child: Text('TÁ LẢ',
              style: TextStyle(
                  color: Color(0xFFF2C24E), fontSize: 30, fontWeight: FontWeight.w800, letterSpacing: 3)),
        ),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFC42E24), Color(0xFF831C16)],
        ),
      );

  Widget _front() => _cardShell(
        Material(
          type: MaterialType.transparency,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Ù!',
                  style: TextStyle(fontSize: 64, fontWeight: FontWeight.w800, color: Color(0xFFC42E24))),
              const SizedBox(height: 8),
              Avatar(id: widget.playerId, name: widget.name, size: 64),
              const SizedBox(height: 12),
              Text(widget.name,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF1C2A24))),
              const SizedBox(height: 6),
              Text(fmtK(widget.amount, sign: true),
                  style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w800, color: Color(0xFF146C43))),
              const SizedBox(height: 14),
              const Text('Chạm để đóng', style: TextStyle(fontSize: 12, color: Color(0xFF5B6B63))),
            ],
          ),
        ),
        color: const Color(0xFFFFFDF7),
      );
}
