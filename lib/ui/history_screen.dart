import 'package:flutter/material.dart';

import '../main.dart';
import '../models.dart';
import '../rules.dart';
import 'log_screen.dart';
import 'widgets.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final p = Pal.of(context);
    return ScreenFrame(
      title: 'Lịch sử ván',
      children: [
        if (s.history.isEmpty)
          FeltPanel(
            child: Text('Chưa có ván nào kết thúc. Ván sẽ vào lịch sử khi có người Ù hoặc khi xếp hạng.',
                style: TextStyle(color: p.onFeltSub, fontSize: 14)),
          ),
        for (final r in s.history) _RoundCard(round: r),
      ],
    );
  }
}

class _RoundCard extends StatefulWidget {
  final Round round;
  const _RoundCard({required this.round});
  @override
  State<_RoundCard> createState() => _RoundCardState();
}

class _RoundCardState extends State<_RoundCard> {
  bool open = false;

  @override
  Widget build(BuildContext context) {
    final s = Ctl.of(context).state;
    final p = Pal.of(context);
    final r = widget.round;
    final last = r.last;
    final ids = List.of(r.playerIds)
      ..sort((a, b) => (r.deltas[b] ?? 0).compareTo(r.deltas[a] ?? 0));

    String chipName(String id) {
      final h = last.hang[id];
      return h == null ? s.nameOf(id) : '${s.nameOf(id)} · ${kTenHang[h]}';
    }

    return Panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Expanded(
                  child: Text(roundTitle(s, r),
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800))),
              Text(hhmm(r.endedAt), style: TextStyle(fontSize: 13, color: p.sub)),
            ],
          ),
          if (last.type == EventType.u)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(last.loserId == null ? 'Không ai đền' : '${s.nameOf(last.loserId)} đền làng',
                  style: TextStyle(fontSize: 13, color: p.sub)),
            ),
          const SizedBox(height: 12),
          const SectionLabel('Tiền ván này'),
          const SizedBox(height: 8),
          TileGrid(gap: 8, columns: last.hang.isEmpty ? 2 : 1, children: [
            for (final id in ids) DeltaChip(name: chipName(id), value: r.deltas[id] ?? 0),
          ]),
          const SizedBox(height: 10),
          Text(
            'Tổng sau ván: ${r.playerIds.map((id) => '${s.nameOf(id)} ${fmtK(r.totalsAfter[id] ?? 0, sign: true)}').join(' · ')}',
            style: TextStyle(fontSize: 13, color: p.sub),
          ),
          const SizedBox(height: 4),
          Divider(color: p.border, height: 16),
          InkWell(
            onTap: () => setState(() => open = !open),
            child: SizedBox(
              height: 44,
              child: Row(
                children: [
                  Expanded(
                    child: Text('Diễn biến (${r.events.length})',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: p.link)),
                  ),
                  Icon(open ? Icons.expand_less_rounded : Icons.expand_more_rounded, color: p.link),
                ],
              ),
            ),
          ),
          if (open)
            for (final e in r.events)
              Padding(padding: const EdgeInsets.only(top: 8), child: EventLine(event: e)),
        ],
      ),
    );
  }
}
