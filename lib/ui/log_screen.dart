import 'package:flutter/material.dart';

import '../main.dart';
import '../models.dart';
import '../rules.dart';
import 'widgets.dart';

String hhmm(DateTime t) =>
    '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';

/// Một dòng diễn biến: giờ, nội dung, số tiền.
class EventLine extends StatelessWidget {
  final GameEvent event;
  final bool onFelt;
  const EventLine({super.key, required this.event, this.onFelt = false});

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final p = Pal.of(context);
    final isGa = event.type == EventType.nopGa;
    final amt = eventAmount(event);
    final amtText = isGa ? 'gà +${fmtK(amt)}' : fmtK(amt, sign: true);
    final Color amtColor = onFelt
        ? (isGa ? const Color(0xFFF3D27A) : const Color(0xFF8EE0B2))
        : (isGa ? const Color(0xFF9A6A00) : p.posFg);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 44,
          child: Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(hhmm(event.time),
                style: TextStyle(fontSize: 12, color: onFelt ? const Color(0xFF9CC4B2) : p.sub)),
          ),
        ),
        Expanded(
          child: Text(describeEvent(s, event),
              style: TextStyle(fontSize: 14, color: onFelt ? p.onFelt : p.text)),
        ),
        const SizedBox(width: 8),
        Text(amtText, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: amtColor)),
      ],
    );
  }
}

/// Toàn bộ diễn biến của ván đang chơi.
class LogScreen extends StatelessWidget {
  const LogScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final p = Pal.of(context);
    final deltas = currentDeltas(s);
    return ScreenFrame(
      title: 'Ván #${s.roundNumber} đang chơi',
      children: [
        Panel(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SectionLabel('Tiền ván này'),
              const SizedBox(height: 12),
              TileGrid(
                gap: 8,
                children: [
                  for (final pl in s.active) DeltaChip(name: pl.name, value: deltas[pl.id] ?? 0),
                ],
              ),
              const SizedBox(height: 10),
              Text('Quỹ gà hiện có: ${fmtK(s.pot)}', style: TextStyle(color: p.sub, fontSize: 13)),
            ],
          ),
        ),
        Panel(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SectionLabel('Diễn biến (${s.current.length})'),
              if (s.current.isEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: Text('Chưa có diễn biến nào.', style: TextStyle(color: p.sub)),
                ),
              for (final e in s.current)
                Padding(padding: const EdgeInsets.only(top: 10), child: EventLine(event: e)),
            ],
          ),
        ),
      ],
    );
  }
}

class DeltaChip extends StatelessWidget {
  final String name;
  final int value;
  const DeltaChip({super.key, required this.name, required this.value});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: value == 0 ? p.chip : p.moneyBg(value),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontWeight: FontWeight.w600, color: p.text)),
          ),
          const SizedBox(width: 6),
          Text(fmtK(value, sign: true),
              style: TextStyle(
                  fontWeight: FontWeight.w800, color: value == 0 ? p.sub : p.moneyFg(value))),
        ],
      ),
    );
  }
}
