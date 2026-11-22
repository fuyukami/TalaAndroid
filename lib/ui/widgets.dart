import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import '../rules.dart';

// ---------------------------------------------------------------------------
// Bảng màu (sáng / tối theo máy)
// ---------------------------------------------------------------------------

class Pal {
  final bool dark;
  const Pal(this.dark);

  static Pal of(BuildContext context) => Pal(Theme.of(context).brightness == Brightness.dark);

  Color get feltTop => dark ? const Color(0xFF10513E) : const Color(0xFF17694F);
  Color get feltMid => dark ? const Color(0xFF0A3A2C) : const Color(0xFF0E4A38);
  Color get feltBottom => dark ? const Color(0xFF06251C) : const Color(0xFF0A3528);
  Color get onFelt => const Color(0xFFFFFDF7);
  Color get onFeltSub => const Color(0xFFB9DCCB);
  Color get feltPanel => const Color(0x8C051E16);

  Color get card => dark ? const Color(0xFF22302A) : const Color(0xFFFFFDF7);
  Color get cardEdge => dark ? const Color(0xFF0F1A16) : const Color(0xFFC9C2AE);
  Color get text => dark ? const Color(0xFFF1EDE2) : const Color(0xFF1C2A24);
  Color get sub => dark ? const Color(0xFFA9BDB3) : const Color(0xFF5B6B63);
  Color get chip => dark ? const Color(0xFF2E3D36) : const Color(0xFFEEE8D8);
  Color get border => dark ? const Color(0xFF3E5048) : const Color(0xFFD6D0BF);
  Color get field => dark ? const Color(0xFF1A2621) : Colors.white;
  Color get posFg => dark ? const Color(0xFF8EE0B2) : const Color(0xFF146C43);
  Color get posBg => dark ? const Color(0xFF1C3D2D) : const Color(0xFFE3F4EA);
  Color get negFg => dark ? const Color(0xFFFFB4AB) : const Color(0xFFB3261E);
  Color get negBg => dark ? const Color(0xFF4A2422) : const Color(0xFFFBE9E7);
  Color get link => dark ? const Color(0xFF9EC2FF) : const Color(0xFF2860C4);

  Color moneyFg(int v) => v < 0 ? negFg : posFg;
  Color moneyBg(int v) => v < 0 ? negBg : posBg;
}

/// Màu nút theo chức năng: (trên, dưới, cạnh đáy, chữ).
class BtnColors {
  final Color top, bottom, edge, fg;
  const BtnColors(this.top, this.bottom, this.edge, [this.fg = Colors.white]);

  static const green = BtnColors(Color(0xFF43B87A), Color(0xFF278A55), Color(0xFF1A5E3A));
  static const pink = BtnColors(Color(0xFFDE3B7A), Color(0xFFAE1450), Color(0xFF760D36));
  static const amber =
      BtnColors(Color(0xFFFFD36B), Color(0xFFEAA623), Color(0xFFA06E0B), Color(0xFF3E2B00));
  static const red = BtnColors(Color(0xFFEE5A4F), Color(0xFFC42E24), Color(0xFF831C16));
  static const blue = BtnColors(Color(0xFF4E8BEA), Color(0xFF2860C4), Color(0xFF1A4288));
  static const ink = BtnColors(Color(0xFF34443D), Color(0xFF1C2A24), Color(0xFF000000));
  static const ivory =
      BtnColors(Color(0xFFFFFDF7), Color(0xFFE6DFCB), Color(0xFFA39C88), Color(0xFF1C2A24));
}

const List<Color> kAvatarColors = [
  Color(0xFF2F6FD6),
  Color(0xFFC2185B),
  Color(0xFFE07B12),
  Color(0xFF127A73),
];

Color avatarColor(String id) {
  final i = int.tryParse(id.replaceAll(RegExp(r'\D'), '')) ?? 1;
  return kAvatarColors[(i - 1) % kAvatarColors.length];
}

String initials(String name) {
  final parts = name.trim().split(RegExp(r'\s+')).where((s) => s.isNotEmpty).toList();
  if (parts.isEmpty) return '?';
  if (parts.length == 1) {
    return parts.first.characters.take(2).toString().toUpperCase();
  }
  final last = parts.last;
  // "Người 1" → "N1"
  return (parts.first.characters.first + last.characters.first).toUpperCase();
}

// ---------------------------------------------------------------------------
// Nền bàn chơi
// ---------------------------------------------------------------------------

class FeltBackground extends StatelessWidget {
  final Widget child;
  const FeltBackground({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: RadialGradient(
          center: const Alignment(0, -1),
          radius: 1.6,
          colors: [p.feltTop, p.feltMid, p.feltBottom],
          stops: const [0, 0.55, 1],
        ),
      ),
      child: child,
    );
  }
}

/// Khung màn hình chung: nền bàn chơi, tiêu đề, nút quay lại.
class ScreenFrame extends StatelessWidget {
  final String title;
  final List<Widget> children;
  final Widget? bottom;
  final bool showBack;

  const ScreenFrame({
    super.key,
    required this.title,
    required this.children,
    this.bottom,
    this.showBack = true,
  });

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Scaffold(
      backgroundColor: p.feltBottom,
      body: FeltBackground(
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                child: Row(
                  children: [
                    if (showBack) ...[
                      GlassIconButton(
                        icon: Icons.chevron_left_rounded,
                        tooltip: 'Quay lại',
                        onPressed: () => Navigator.of(context).maybePop(),
                      ),
                      const SizedBox(width: 12),
                    ],
                    Expanded(
                      child: Text(title,
                          style: TextStyle(
                              fontSize: 24, fontWeight: FontWeight.w800, color: p.onFelt)),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                  children: _spaced(children, 16),
                ),
              ),
              if (bottom != null)
                Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 16), child: bottom),
            ],
          ),
        ),
      ),
    );
  }
}

List<Widget> _spaced(List<Widget> items, double gap) {
  final out = <Widget>[];
  for (var i = 0; i < items.length; i++) {
    if (i > 0) out.add(SizedBox(height: gap));
    out.add(items[i]);
  }
  return out;
}

class GlassIconButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final VoidCallback onPressed;
  const GlassIconButton(
      {super.key, required this.icon, required this.tooltip, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Tooltip(
      message: tooltip,
      child: Material(
        color: Colors.white.withValues(alpha: 0.08),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.18)),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onPressed,
          child: SizedBox(width: 48, height: 48, child: Icon(icon, color: p.onFelt)),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Thẻ nổi (nền ngà, bóng đổ nhiều lớp)
// ---------------------------------------------------------------------------

class Panel extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? outline;
  const Panel({super.key, required this.child, this.padding = const EdgeInsets.all(16), this.outline});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: p.card,
        borderRadius: BorderRadius.circular(20),
        border: outline != null ? Border.all(color: outline!, width: 2) : null,
        boxShadow: [
          BoxShadow(color: p.cardEdge, offset: const Offset(0, 6)),
          const BoxShadow(color: Color(0x59000000), offset: Offset(0, 16), blurRadius: 26),
        ],
      ),
      child: DefaultTextStyle.merge(style: TextStyle(color: p.text), child: child),
    );
  }
}

/// Khung tối trong suốt trên nền bàn chơi.
class FeltPanel extends StatelessWidget {
  final Widget child;
  const FeltPanel({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: p.feltPanel,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
      ),
      child: DefaultTextStyle.merge(style: TextStyle(color: p.onFelt), child: child),
    );
  }
}

class SectionLabel extends StatelessWidget {
  final String text;
  final bool onFelt;
  const SectionLabel(this.text, {super.key, this.onFelt = false});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Text(text.toUpperCase(),
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.0,
          color: onFelt ? p.onFeltSub : p.sub,
        ));
  }
}

// ---------------------------------------------------------------------------
// Nút bấm kiểu phím nổi: lún xuống khi bấm, kèm rung nhẹ
// ---------------------------------------------------------------------------

class Raised3DButton extends StatefulWidget {
  final String label;
  final BtnColors colors;
  final VoidCallback? onPressed;
  final double height;
  final double fontSize;
  final Widget? leading;

  const Raised3DButton({
    super.key,
    required this.label,
    required this.colors,
    required this.onPressed,
    this.height = 60,
    this.fontSize = 16,
    this.leading,
  });

  @override
  State<Raised3DButton> createState() => _Raised3DButtonState();
}

class _Raised3DButtonState extends State<Raised3DButton> {
  bool _down = false;
  static const double depth = 6;

  void _set(bool v) {
    if (widget.onPressed == null) return;
    if (_down != v) setState(() => _down = v);
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.colors;
    final enabled = widget.onPressed != null;
    final dy = _down ? depth - 1 : 0.0;
    return Semantics(
      button: true,
      enabled: enabled,
      label: widget.label,
      excludeSemantics: true,
      child: GestureDetector(
        onTapDown: (_) => _set(true),
        onTapUp: (_) => _set(false),
        onTapCancel: () => _set(false),
        onTap: enabled
            ? () {
                HapticFeedback.lightImpact();
                widget.onPressed!();
              }
            : null,
        child: Opacity(
          opacity: enabled ? 1 : 0.45,
          child: SizedBox(
            height: widget.height + depth,
            child: Stack(
              children: [
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  height: widget.height,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: c.edge,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: _down
                          ? const []
                          : const [
                              BoxShadow(
                                  color: Color(0x4D000000), offset: Offset(0, 8), blurRadius: 14)
                            ],
                    ),
                  ),
                ),
                AnimatedPositioned(
                  duration: const Duration(milliseconds: 70),
                  left: 0,
                  right: 0,
                  top: dy,
                  height: widget.height,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [c.top, c.bottom],
                      ),
                      border: Border(
                          top: BorderSide(color: Colors.white.withValues(alpha: 0.35), width: 1)),
                    ),
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (widget.leading != null) ...[
                              IconTheme(
                                  data: IconThemeData(color: c.fg, size: 20),
                                  child: widget.leading!),
                              const SizedBox(width: 8),
                            ],
                            Flexible(
                              child: Text(
                                widget.label,
                                textAlign: TextAlign.center,
                                maxLines: 2,
                                style: TextStyle(
                                  color: c.fg,
                                  fontSize: widget.fontSize,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.3,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Nút phẳng mờ trên nền bàn chơi.
class GlassButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final double height;
  const GlassButton({super.key, required this.label, required this.onPressed, this.height = 50});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return SizedBox(
      height: height,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: p.onFelt,
          backgroundColor: Colors.white.withValues(alpha: 0.10),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.22)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: const TextStyle(fontFamily: 'BeVietnamPro', fontSize: 15, fontWeight: FontWeight.w700),
        ),
        child: Text(label, textAlign: TextAlign.center),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Ô chọn (chip) người chơi / lựa chọn
// ---------------------------------------------------------------------------

class ChoiceTile extends StatelessWidget {
  final String label;
  final String? hint;
  final bool selected;
  final VoidCallback? onTap;
  final BtnColors? selectedColors;
  final bool showCheck;

  const ChoiceTile({
    super.key,
    required this.label,
    this.hint,
    required this.selected,
    required this.onTap,
    this.selectedColors,
    this.showCheck = true,
  });

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    final enabled = onTap != null;
    final c = selectedColors ?? (p.dark ? BtnColors.ivory : BtnColors.ink);
    return Semantics(
      selected: selected,
      button: true,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        constraints: const BoxConstraints(minHeight: 52),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          gradient: selected
              ? LinearGradient(
                  begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [c.top, c.bottom])
              : null,
          color: selected ? null : p.field,
          border: selected ? null : Border.all(color: p.border, width: 1.5),
          boxShadow: selected ? [BoxShadow(color: c.edge, offset: const Offset(0, 4))] : null,
        ),
        child: Material(
          type: MaterialType.transparency,
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: enabled
                ? () {
                    HapticFeedback.selectionClick();
                    onTap!();
                  }
                : null,
            child: Opacity(
              opacity: enabled || selected ? 1 : 0.4,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      selected && showCheck ? '✓ $label' : label,
                      maxLines: 1,
                      overflow: TextOverflow.fade,
                      softWrap: false,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: selected ? FontWeight.w800 : FontWeight.w700,
                        color: selected ? c.fg : p.text,
                      ),
                    ),
                    if (hint != null)
                      Text(hint!,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              fontSize: 12, color: selected ? c.fg.withValues(alpha: 0.85) : p.sub)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Lưới 2 cột (hoặc [columns] cột) cho các ô chọn.
class TileGrid extends StatelessWidget {
  final List<Widget> children;
  final int columns;
  final double gap;
  const TileGrid({super.key, required this.children, this.columns = 2, this.gap = 10});

  @override
  Widget build(BuildContext context) {
    final rows = <Widget>[];
    for (var i = 0; i < children.length; i += columns) {
      final row = <Widget>[];
      for (var j = 0; j < columns; j++) {
        if (j > 0) row.add(SizedBox(width: gap));
        row.add(Expanded(child: i + j < children.length ? children[i + j] : const SizedBox()));
      }
      if (rows.isNotEmpty) rows.add(SizedBox(height: gap));
      rows.add(IntrinsicHeight(
          child: Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: row)));
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: rows);
  }
}

// ---------------------------------------------------------------------------
// Số tiền có hiệu ứng chạy
// ---------------------------------------------------------------------------

class AnimatedMoney extends StatelessWidget {
  final int value;
  final TextStyle style;
  final bool sign;
  final Color Function(int v)? colorFor;
  const AnimatedMoney(
      {super.key, required this.value, required this.style, this.sign = true, this.colorFor});

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(end: value.toDouble()),
      duration: const Duration(milliseconds: 650),
      curve: Curves.easeOutCubic,
      builder: (context, v, _) {
        final n = v.round();
        return Text(
          fmtK(n, sign: sign),
          style: colorFor == null ? style : style.copyWith(color: colorFor!(n)),
        );
      },
    );
  }
}

class MoneyPill extends StatelessWidget {
  final String text;
  final int value;
  const MoneyPill({super.key, required this.text, required this.value});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: p.moneyBg(value), borderRadius: BorderRadius.circular(999)),
      child: Text(text,
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: p.moneyFg(value))),
    );
  }
}

class Avatar extends StatelessWidget {
  final String id;
  final String name;
  final double size;
  const Avatar({super.key, required this.id, required this.name, this.size = 40});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: avatarColor(id),
        boxShadow: const [BoxShadow(color: Color(0x33000000), offset: Offset(0, 2), blurRadius: 3)],
      ),
      child: Text(initials(name),
          style: TextStyle(
              color: Colors.white, fontWeight: FontWeight.w800, fontSize: size * 0.37)),
    );
  }
}

// ---------------------------------------------------------------------------
// Thẻ nghiêng 3D: hơi ngả ra sau, chạm vào thì nghiêng về phía ngón tay
// ---------------------------------------------------------------------------

class Tilt3D extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double restTilt;
  const Tilt3D({super.key, required this.child, this.onTap, this.restTilt = 0.10});

  @override
  State<Tilt3D> createState() => _Tilt3DState();
}

class _Tilt3DState extends State<Tilt3D> {
  Offset _touch = Offset.zero; // -1..1
  bool _down = false;

  void _update(Offset local, Size size) {
    setState(() {
      _down = true;
      _touch = Offset(
        (local.dx / size.width * 2 - 1).clamp(-1, 1),
        (local.dy / size.height * 2 - 1).clamp(-1, 1),
      );
    });
  }

  void _release() => setState(() {
        _down = false;
        _touch = Offset.zero;
      });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (d) => _update(d.localPosition, context.size ?? const Size(160, 160)),
      onTapUp: (_) => _release(),
      onTapCancel: _release,
      onTap: widget.onTap,
      child: TweenAnimationBuilder<Offset>(
        tween: Tween(end: _down ? _touch : Offset.zero),
        duration: const Duration(milliseconds: 180),
        builder: (context, t, child) {
          final m = Matrix4.identity()
            ..setEntry(3, 2, 0.0014)
            ..rotateX(widget.restTilt - t.dy * 0.12)
            ..rotateY(t.dx * 0.16);
          if (_down) m.multiply(Matrix4.diagonal3Values(0.98, 0.98, 1));
          return Transform(transform: m, alignment: Alignment.center, child: child);
        },
        child: widget.child,
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Thông báo & hộp hỏi
// ---------------------------------------------------------------------------

void showMsg(BuildContext context, String text, {bool error = false}) {
  final m = ScaffoldMessenger.of(context);
  m.hideCurrentSnackBar();
  m.showSnackBar(SnackBar(
    content: Text(text, style: const TextStyle(fontSize: 15)),
    backgroundColor: error ? const Color(0xFFB3261E) : const Color(0xFF1C2A24),
    behavior: SnackBarBehavior.floating,
    duration: Duration(milliseconds: error ? 3500 : 2200),
  ));
}

Future<bool> confirm(BuildContext context,
    {required String title, required String message, String ok = 'Đồng ý', bool danger = false}) async {
  final r = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(title),
      content: Text(message),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Huỷ')),
        FilledButton(
          style: danger ? FilledButton.styleFrom(backgroundColor: const Color(0xFFC42E24)) : null,
          onPressed: () => Navigator.pop(ctx, true),
          child: Text(ok),
        ),
      ],
    ),
  );
  return r ?? false;
}

// ---------------------------------------------------------------------------
// Pháo hoa giấy
// ---------------------------------------------------------------------------

class ConfettiPainter extends CustomPainter {
  final double t; // 0..1
  final List<ConfettiBit> bits;
  ConfettiPainter(this.t, this.bits);

  static List<ConfettiBit> make(int n, int seed) {
    final r = math.Random(seed);
    const colors = [
      Color(0xFFF2C24E),
      Color(0xFFEE5A4F),
      Color(0xFF43B87A),
      Color(0xFF4E8BEA),
      Color(0xFFDE3B7A),
      Colors.white,
    ];
    return List.generate(
      n,
      (_) => ConfettiBit(
        x: r.nextDouble(),
        delay: r.nextDouble() * 0.35,
        speed: 0.8 + r.nextDouble() * 0.7,
        drift: (r.nextDouble() - 0.5) * 0.3,
        spin: (r.nextDouble() - 0.5) * 18,
        size: 6 + r.nextDouble() * 6,
        color: colors[r.nextInt(colors.length)],
      ),
    );
  }

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();
    for (final b in bits) {
      final lt = ((t - b.delay) / (1 - b.delay)).clamp(0.0, 1.0);
      if (lt <= 0) continue;
      final y = -20 + lt * b.speed * (size.height + 40);
      final x = (b.x + b.drift * lt) * size.width + math.sin(lt * 12 + b.x * 6) * 12;
      paint.color = b.color.withValues(alpha: (1 - lt * 0.6).clamp(0.0, 1.0));
      canvas.save();
      canvas.translate(x, y);
      canvas.rotate(b.spin * lt);
      final squash = math.cos(lt * 10 + b.x * 5).abs() * 0.8 + 0.2;
      canvas.drawRect(
          Rect.fromCenter(center: Offset.zero, width: b.size, height: b.size * 0.55 * squash),
          paint);
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(ConfettiPainter old) => old.t != t;
}

class ConfettiBit {
  final double x, delay, speed, drift, spin, size;
  final Color color;
  ConfettiBit({
    required this.x,
    required this.delay,
    required this.speed,
    required this.drift,
    required this.spin,
    required this.size,
    required this.color,
  });
}
