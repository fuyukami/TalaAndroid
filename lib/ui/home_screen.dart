import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../main.dart';
import '../models.dart';
import '../rules.dart';
import 'action_screens.dart';
import 'history_screen.dart';
import 'log_screen.dart';
import 'settings_screen.dart';
import 'widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Future<void> _exit() async {
    final ok = await confirm(context,
        title: 'Thoát app?', message: 'Dữ liệu đã được lưu. Mở lại app sẽ tiếp tục đúng chỗ này.', ok: 'Thoát');
    if (!ok || !mounted) return;
    await Ctl.read(context).save();
    await SystemNavigator.pop();
  }


  Future<void> _go(Widget screen) =>
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => screen));

  void _undo() => Ctl.read(context).undo();

  Future<void> _reset() async {
    final ok = await confirm(context,
        title: 'Reset toàn bộ?',
        message: 'Đưa tiền mọi người và quỹ gà về 0, xoá lịch sử. Có thể bấm Hoàn tác nếu lỡ tay.',
        ok: 'Reset',
        danger: true);
    if (ok && mounted) {
      Ctl.read(context).reset();
    }
  }

  Future<void> _rename(Player pl) async {
    final c = Ctl.read(context);
    final tf = TextEditingController(text: pl.name);
    String? err;
    await showDialog<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setD) {
          void save() {
            final e = c.rename(pl.id, tf.text);
            if (e != null) {
              setD(() => err = e);
            } else {
              Navigator.pop(ctx);
            }
          }

          return AlertDialog(
            title: const Text('Đổi tên'),
            content: TextField(
              controller: tf,
              autofocus: true,
              maxLength: 20,
              textCapitalization: TextCapitalization.words,
              decoration: InputDecoration(labelText: 'Tên mới', errorText: err),
              onSubmitted: (_) => save(),
            ),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Huỷ')),
              FilledButton(onPressed: save, child: const Text('Lưu')),
            ],
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = Ctl.of(context);
    final s = c.state;
    final p = Pal.of(context);
    final deltas = currentDeltas(s);
    final players = s.active;
    final leaderMoney = players.map((x) => x.money).reduce((a, b) => a > b ? a : b);
    final hasLeader = players.where((x) => x.money == leaderMoney).length == 1 && leaderMoney > 0;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _exit();
      },
      child: Scaffold(
        backgroundColor: p.feltBottom,
        body: FeltBackground(
          child: SafeArea(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
              children: [
                // Tiêu đề
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('VÁN #${s.roundNumber} · ${s.current.isEmpty ? 'CHƯA CÓ DIỄN BIẾN' : 'ĐANG CHƠI'}',
                              style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 1.4,
                                  color: p.onFeltSub)),
                          Text('TÁ LẢ PRO',
                              style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.5,
                                  color: p.onFelt)),
                        ],
                      ),
                    ),
                    GlassIconButton(
                        icon: Icons.power_settings_new_rounded, tooltip: 'Thoát app', onPressed: _exit),
                  ],
                ),
                const SizedBox(height: 16),

                // Cược & quỹ gà
                Row(
                  children: [
                    Expanded(child: _StatTile(label: 'MỨC CƯỢC', value: '${s.settings.bet}K')),
                    const SizedBox(width: 12),
                    Expanded(child: _StatTile(label: 'QUỸ GÀ', value: '${s.pot}K', gold: true)),
                  ],
                ),
                const SizedBox(height: 18),

                // Người chơi
                TileGrid(
                  gap: 12,
                  children: [
                    for (final pl in players)
                      _PlayerCard(
                        player: pl,
                        roundDelta: deltas[pl.id] ?? 0,
                        leader: hasLeader && pl.money == leaderMoney,
                        onTap: () => _rename(pl),
                      ),
                  ],
                ),
                const SizedBox(height: 18),

                // Diễn biến ván hiện tại
                FeltPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          const Expanded(child: SectionLabel('Diễn biến ván hiện tại', onFelt: true)),
                          if (s.current.isNotEmpty)
                            TextButton(
                              onPressed: () => _go(const LogScreen()),
                              style: TextButton.styleFrom(foregroundColor: const Color(0xFFF3D27A)),
                              child: Text('Xem hết (${s.current.length})'),
                            ),
                        ],
                      ),
                      if (s.current.isEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: 6),
                          child: Text('Chưa có gì. Ăn cây, ăn chốt, nộp gà sẽ hiện ở đây.',
                              style: TextStyle(color: p.onFeltSub, fontSize: 14)),
                        )
                      else
                        for (final e in s.current.reversed.take(3))
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: EventLine(event: e, onFelt: true),
                          ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),

                // Nút chức năng
                TileGrid(
                  gap: 12,
                  children: [
                    Raised3DButton(
                        label: 'ĂN CÂY',
                        colors: BtnColors.green,
                        onPressed: () => _go(const AnCayScreen())),
                    Raised3DButton(
                        label: 'ĂN CHỐT',
                        colors: BtnColors.pink,
                        onPressed: () => _go(const AnChotScreen())),
                    Raised3DButton(
                        label: 'NỘP GÀ',
                        colors: BtnColors.amber,
                        onPressed: () => _go(const NopGaScreen())),
                    Raised3DButton(
                        label: 'XỬ LÝ Ù', colors: BtnColors.red, onPressed: () => _go(const UScreen())),
                  ],
                ),
                const SizedBox(height: 12),
                Raised3DButton(
                    label: 'XẾP HẠNG & KẾT THÚC VÁN',
                    colors: BtnColors.blue,
                    onPressed: () => _go(const XepHangScreen())),
                const SizedBox(height: 14),

                if (c.canUndo) ...[
                  _UndoButton(label: c.undoLabel!, onPressed: _undo),
                  const SizedBox(height: 14),
                ],

                Row(
                  children: [
                    Expanded(child: GlassButton(label: 'Lịch sử', onPressed: () => _go(const HistoryScreen()))),
                    const SizedBox(width: 10),
                    Expanded(child: GlassButton(label: 'Cài đặt', onPressed: () => _go(const SettingsScreen()))),
                    const SizedBox(width: 10),
                    Expanded(child: GlassButton(label: 'Reset', onPressed: _reset)),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  final String label;
  final String value;
  final bool gold;
  const _StatTile({required this.label, required this.value, this.gold = false});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        color: gold ? null : p.card,
        gradient: gold
            ? const LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0xFFFFE7A3), Color(0xFFF2C24E)])
            : null,
        boxShadow: [
          BoxShadow(color: gold ? const Color(0xFFB68A1E) : p.cardEdge, offset: const Offset(0, 6)),
          const BoxShadow(color: Color(0x59000000), offset: Offset(0, 14), blurRadius: 24),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label,
              style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1,
                  color: gold ? const Color(0xFF6A4A00) : p.sub)),
          Text(value,
              style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: gold ? const Color(0xFF3E2B00) : p.text)),
        ],
      ),
    );
  }
}

class _PlayerCard extends StatelessWidget {
  final Player player;
  final int roundDelta;
  final bool leader;
  final VoidCallback onTap;
  const _PlayerCard(
      {required this.player, required this.roundDelta, required this.leader, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Tilt3D(
      onTap: onTap,
      child: Semantics(
        button: true,
        label: '${player.name}, tổng ${fmtK(player.money, sign: true)}. Chạm để đổi tên',
        excludeSemantics: true,
        child: Panel(
          padding: const EdgeInsets.all(14),
          outline: leader ? const Color(0xFFF2C24E) : null,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Avatar(id: player.id, name: player.name),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(player.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
                  ),
                  if (leader)
                    const Icon(Icons.workspace_premium_rounded, color: Color(0xFFE0A91C), size: 22),
                ],
              ),
              const SizedBox(height: 10),
              AnimatedMoney(
                value: player.money,
                colorFor: p.moneyFg,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              MoneyPill(text: 'Ván này ${fmtK(roundDelta, sign: true)}', value: roundDelta),
            ],
          ),
        ),
      ),
    );
  }
}

class _UndoButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  const _UndoButton({required this.label, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    return Material(
      color: Colors.white.withValues(alpha: 0.06),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: p.onFelt.withValues(alpha: 0.55), width: 1.5),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          HapticFeedback.mediumImpact();
          onPressed();
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Icon(Icons.undo_rounded, color: p.onFelt),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('HOÀN TÁC',
                        style: TextStyle(color: p.onFelt, fontSize: 15, fontWeight: FontWeight.w700)),
                    Text(label,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(color: p.onFeltSub, fontSize: 13)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
