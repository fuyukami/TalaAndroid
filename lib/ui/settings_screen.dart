import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../main.dart';
import '../models.dart';
import 'widgets.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late Settings st;
  late Map<String, TextEditingController> names;
  late TextEditingController bet;
  late Map<String, TextEditingController> heSo;
  bool _init = false;
  bool dirty = false;

  static const _keys = [
    'uMoiNguoi',
    'anCay0', 'anCay1', 'anCay2',
    'anChot',
    'nopGa0', 'nopGa1', 'nopGa2',
    'xepHang0', 'xepHang1', 'xepHang2',
    'mom',
  ];

  Map<String, int> _values(Settings s) => {
        'uMoiNguoi': s.uMoiNguoi,
        'anCay0': s.anCay[0],
        'anCay1': s.anCay[1],
        'anCay2': s.anCay[2],
        'anChot': s.anChot,
        'nopGa0': s.nopGa[0],
        'nopGa1': s.nopGa[1],
        'nopGa2': s.nopGa[2],
        'xepHang0': s.xepHang[0],
        'xepHang1': s.xepHang[1],
        'xepHang2': s.xepHang[2],
        'mom': s.mom,
      };

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_init) return;
    _init = true;
    final c = Ctl.read(context);
    st = c.state.settings.copy();
    names = {for (final p in c.state.players) p.id: _tc(p.name)};
    bet = _tc('${st.bet}');
    final v = _values(st);
    heSo = {for (final k in _keys) k: _tc('${v[k]}')};
  }

  TextEditingController _tc(String v) => TextEditingController(text: v)..addListener(_markDirty);

  void _markDirty() {
    if (mounted) setState(() => dirty = true);
  }

  @override
  void dispose() {
    for (final t in [...names.values, bet, ...heSo.values]) {
      t.dispose();
    }
    super.dispose();
  }

  void _defaults() {
    final d = _values(Settings());
    for (final k in _keys) {
      heSo[k]!.text = '${d[k]}';
    }
  }

  Settings? _collect() {
    int? n(TextEditingController t) => int.tryParse(t.text.trim());
    final b = n(bet);
    final vals = {for (final k in _keys) k: n(heSo[k]!)};
    if (b == null || vals.values.any((v) => v == null)) return null;
    return Settings(
      playerCount: st.playerCount,
      bet: b,
      uMoiNguoi: vals['uMoiNguoi']!,
      anCay: [vals['anCay0']!, vals['anCay1']!, vals['anCay2']!],
      anChot: vals['anChot']!,
      nopGa: [vals['nopGa0']!, vals['nopGa1']!, vals['nopGa2']!],
      xepHang: [vals['xepHang0']!, vals['xepHang1']!, vals['xepHang2']!],
      mom: vals['mom']!,
    );
  }

  void _save() {
    final s = _collect();
    if (s == null) {
      showMsg(context, 'Mức cược và hệ số phải là số nguyên.', error: true);
      return;
    }
    final err = Ctl.read(context)
        .updateSettings(s, {for (final e in names.entries) e.key: e.value.text});
    if (err != null) {
      showMsg(context, err, error: true);
      return;
    }
    dirty = false;
    final m = ScaffoldMessenger.of(context);
    Navigator.of(context).pop();
    m.hideCurrentSnackBar();
    m.showSnackBar(const SnackBar(
        content: Text('Đã lưu cài đặt'),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Color(0xFF1C2A24)));
  }

  @override
  Widget build(BuildContext context) {
    final p = Pal.of(context);
    final c = Ctl.of(context);
    final midGame = c.state.current.isNotEmpty;
    final others = st.playerCount - 1;
    final bv = int.tryParse(bet.text) ?? 0;
    final uv = int.tryParse(heSo['uMoiNguoi']!.text) ?? 0;

    return PopScope(
      canPop: !dirty,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        final nav = Navigator.of(context);
        final ok = await confirm(context,
            title: 'Bỏ thay đổi?', message: 'Các thay đổi chưa lưu sẽ mất.', ok: 'Bỏ');
        if (ok) {
          setState(() => dirty = false);
          nav.pop();
        }
      },
      child: ScreenFrame(
        title: 'Cài đặt',
        bottom: Raised3DButton(label: 'LƯU CÀI ĐẶT', colors: BtnColors.green, onPressed: _save, height: 58),
        children: [
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Người chơi'),
              const SizedBox(height: 12),
              TileGrid(columns: 3, gap: 8, children: [
                for (var k = kMinPlayers; k <= kMaxPlayers; k++)
                  ChoiceTile(
                    label: '$k người',
                    selected: st.playerCount == k,
                    onTap: midGame && k != c.state.settings.playerCount
                        ? null
                        : () => setState(() {
                              st.playerCount = k;
                              dirty = true;
                            }),
                  ),
              ]),
              if (midGame)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text('Ván đang chơi dở, kết thúc ván rồi mới đổi được số người.',
                      style: TextStyle(fontSize: 12, color: p.sub)),
                ),
              const SizedBox(height: 12),
              for (final pl in c.state.players.take(st.playerCount))
                Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: TextField(
                    controller: names[pl.id],
                    maxLength: 20,
                    textCapitalization: TextCapitalization.words,
                    decoration: _dec(context, 'Tên người chơi ${pl.id.substring(1)}'),
                  ),
                ),
              Text('Không được đặt trùng tên.', style: TextStyle(fontSize: 12, color: p.sub)),
            ]),
          ),
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Mức cược'),
              const SizedBox(height: 12),
              Row(children: [
                SizedBox(width: 130, child: _numField(context, bet, big: true, label: 'Mức cược')),
                const SizedBox(width: 12),
                Text('nghìn đồng', style: TextStyle(fontSize: 15, color: p.text)),
              ]),
            ]),
          ),
          Panel(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              const SectionLabel('Hệ số tiền (× mức cược)'),
              const SizedBox(height: 4),
              _row(context, 'Ù, mỗi người trả', ['uMoiNguoi'],
                  hint: 'Ù nhận = cược × $uv × $others người = ${bv * uv * others}k. '
                      'Có người đền thì người đó trả hết.'),
              _row(context, 'Ăn cây lần 1 / 2 / 3', ['anCay0', 'anCay1', 'anCay2']),
              _row(context, 'Ăn chốt', ['anChot']),
              _row(context, 'Nộp gà lần 1 / 2 / 3', ['nopGa0', 'nopGa1', 'nopGa2']),
              _row(context, 'Nhì / Ba / Bét', ['xepHang0', 'xepHang1', 'xepHang2']),
              _row(context, 'Móm', ['mom'], last: true),
              Align(
                alignment: Alignment.centerLeft,
                child: TextButton(onPressed: _defaults, child: const Text('Khôi phục hệ số mặc định')),
              ),
            ]),
          ),
        ],
      ),
    );
  }

  InputDecoration _dec(BuildContext context, String label) {
    final p = Pal.of(context);
    return InputDecoration(
      labelText: label,
      counterText: '',
      filled: true,
      fillColor: p.field,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
    );
  }

  Widget _numField(BuildContext context, TextEditingController t, {bool big = false, String? label}) {
    final p = Pal.of(context);
    return TextField(
      controller: t,
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly, LengthLimitingTextInputFormatter(4)],
      textAlign: TextAlign.center,
      style: TextStyle(fontSize: big ? 20 : 16, fontWeight: FontWeight.w800, color: p.text),
      decoration: InputDecoration(
        isDense: true,
        filled: true,
        fillColor: p.chip,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
        contentPadding: EdgeInsets.symmetric(horizontal: 6, vertical: big ? 14 : 12),
      ),
    );
  }

  Widget _row(BuildContext context, String label, List<String> keys, {String? hint, bool last = false}) {
    final p = Pal.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
          border: last ? null : Border(bottom: BorderSide(color: p.chip))),
      child: Row(
        children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(label, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: p.text)),
              if (hint != null) Text(hint, style: TextStyle(fontSize: 12, color: p.sub)),
            ]),
          ),
          const SizedBox(width: 8),
          for (var i = 0; i < keys.length; i++) ...[
            if (i > 0) const SizedBox(width: 6),
            SizedBox(width: 48, child: _numField(context, heSo[keys[i]]!, label: label)),
          ],
        ],
      ),
    );
  }
}
