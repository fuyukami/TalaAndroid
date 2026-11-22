import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tala_pro/controller.dart';
import 'package:tala_pro/models.dart';
import 'package:tala_pro/rules.dart';
import 'package:tala_pro/storage.dart';

GameState fresh({int players = 4, int bet = 10}) {
  final s = GameState.initial();
  s.settings.playerCount = players;
  s.settings.bet = bet;
  return s;
}

int money(GameState s, String id) => s.byId(id).money;

int sumWithPot(GameState s) => s.players.fold<int>(0, (a, p) => a + p.money) + s.pot;

void must(GameState s, RuleResult r) {
  expect(r.error, isNull);
  applyEvent(s, r.event!);
}

void main() {
  group('Ăn cây', () {
    test('lần 1/2/3 theo hệ số 1/2/4, tối đa 3 lần', () {
      final s = fresh();
      must(s, buildAnCay(s, 'p1', 'p2'));
      must(s, buildAnCay(s, 'p1', 'p2'));
      must(s, buildAnCay(s, 'p1', 'p2'));
      expect(money(s, 'p1'), -70);
      expect(money(s, 'p2'), 70);
      expect(buildAnCay(s, 'p1', 'p2').error, contains('tối đa 3'));
    });

    test('đã có người ăn thì chỉ người đó ăn tiếp', () {
      final s = fresh();
      must(s, buildAnCay(s, 'p1', 'p2'));
      expect(anCayWinnersFor(s, 'p1').map((p) => p.id), ['p2']);
      expect(buildAnCay(s, 'p1', 'p3').ok, isFalse);
    });

    test('người đã ăn cây của người khác không được ăn cây người mới', () {
      final s = fresh();
      must(s, buildAnCay(s, 'p1', 'p2'));
      expect(anCayWinnersFor(s, 'p3').map((p) => p.id), ['p1', 'p4']);
    });

    test('đổi tên giữa ván không ảnh hưởng đếm cây', () {
      final c = GameController(state: fresh());
      c.apply(buildAnCay(c.state, 'p1', 'p2'));
      expect(c.rename('p1', 'Tuấn'), isNull);
      expect(anCayCount(c.state, 'p1'), 1);
      c.apply(buildAnCay(c.state, 'p1', 'p2'));
      expect(money(c.state, 'p1'), -30);
    });
  });

  group('Ăn chốt', () {
    test('cược × 4', () {
      final s = fresh();
      must(s, buildAnChot(s, 'p3', 'p4'));
      expect(money(s, 'p3'), -40);
      expect(money(s, 'p4'), 40);
    });
  });

  group('Nộp gà', () {
    test('lần 1/2/3 theo 1/2/4 vào quỹ, tối đa 3 lần', () {
      final s = fresh();
      must(s, buildNopGa(s, 'p1'));
      must(s, buildNopGa(s, 'p1'));
      must(s, buildNopGa(s, 'p1'));
      expect(money(s, 'p1'), -70);
      expect(s.pot, 70);
      expect(buildNopGa(s, 'p1').error, contains('tối đa 3'));
      expect(sumWithPot(s), 0);
    });
  });

  group('Ù', () {
    test('4 người, không ai đền: mỗi người trả 50k, Ù nhận 150k (giống app cũ)', () {
      final s = fresh();
      must(s, buildU(s, 'p2', null));
      expect(money(s, 'p2'), 150);
      expect(money(s, 'p1'), -50);
      expect(money(s, 'p3'), -50);
      expect(money(s, 'p4'), -50);
    });

    test('4 người, có người đền: người đền trả 150k', () {
      final s = fresh();
      must(s, buildU(s, 'p2', 'p3'));
      expect(money(s, 'p2'), 150);
      expect(money(s, 'p3'), -150);
      expect(money(s, 'p1'), 0);
    });

    test('3 người: Ù nhận cược × 5 × 2', () {
      final s = fresh(players: 3);
      must(s, buildU(s, 'p1', null));
      expect(money(s, 'p1'), 100);
      expect(money(s, 'p2'), -50);
      expect(money(s, 'p4'), 0);
    });

    test('2 người: Ù nhận cược × 5 × 1', () {
      final s = fresh(players: 2);
      must(s, buildU(s, 'p1', null));
      expect(money(s, 'p1'), 50);
      expect(money(s, 'p2'), -50);
    });

    test('Ù ăn luôn quỹ gà và đóng ván', () {
      final s = fresh();
      must(s, buildNopGa(s, 'p3'));
      must(s, buildU(s, 'p2', null));
      expect(s.pot, 0);
      expect(money(s, 'p2'), 160);
      expect(money(s, 'p3'), -60);
      expect(s.current, isEmpty);
      expect(s.history.length, 1);
      expect(s.history.first.deltas, {'p1': -50, 'p2': 160, 'p3': -60, 'p4': -50});
      expect(sumWithPot(s), 0);
    });

    test('không cho Ù tự đền', () {
      final s = fresh();
      expect(buildU(s, 'p1', 'p1').ok, isFalse);
    });
  });

  group('Xếp hạng', () {
    test('Nhì/Ba/Bét = 1/2/3', () {
      final s = fresh();
      must(s, buildXepHang(s, {'p4': Hang.nhat, 'p1': Hang.nhi, 'p2': Hang.ba, 'p3': Hang.bet}));
      expect(money(s, 'p4'), 60);
      expect(money(s, 'p1'), -10);
      expect(money(s, 'p2'), -20);
      expect(money(s, 'p3'), -30);
      expect(s.history.first.totalsAfter['p4'], 60);
    });

    test('Móm × 4, những người còn lại là Nhì, Ba', () {
      final s = fresh();
      must(s, buildXepHang(s, {'p1': Hang.nhat, 'p2': Hang.mom, 'p3': Hang.nhi, 'p4': Hang.ba}));
      expect(money(s, 'p1'), 70);
      expect(money(s, 'p2'), -40);
      expect(money(s, 'p3'), -10);
      expect(money(s, 'p4'), -20);
    });

    test('cả ba móm', () {
      final s = fresh();
      must(s, buildXepHang(s, {'p1': Hang.nhat, 'p2': Hang.mom, 'p3': Hang.mom, 'p4': Hang.mom}));
      expect(money(s, 'p1'), 120);
    });

    test('báo lỗi khi hai người Nhất, trùng hạng, hoặc nhảy hạng', () {
      final s = fresh();
      expect(validateXepHang(s, {'p1': Hang.nhat, 'p2': Hang.nhat, 'p3': Hang.nhi, 'p4': Hang.ba}),
          isNotNull);
      expect(validateXepHang(s, {'p1': Hang.nhat, 'p2': Hang.nhi, 'p3': Hang.nhi, 'p4': Hang.ba}),
          isNotNull);
      expect(validateXepHang(s, {'p1': Hang.nhat, 'p2': Hang.mom, 'p3': Hang.nhi, 'p4': Hang.bet}),
          isNotNull);
      expect(validateXepHang(s, {'p1': Hang.nhat, 'p2': Hang.nhi}), isNotNull);
    });

    test('xếp hạng không động vào quỹ gà, tiền cộng dồn cả ván', () {
      final s = fresh();
      must(s, buildNopGa(s, 'p1'));
      must(s, buildAnCay(s, 'p2', 'p3'));
      must(s, buildXepHang(s, {'p3': Hang.nhat, 'p1': Hang.nhi, 'p2': Hang.ba, 'p4': Hang.bet}));
      expect(s.pot, 10);
      expect(s.history.first.deltas, {'p1': -20, 'p2': -30, 'p3': 70, 'p4': -30});
      expect(s.history.first.events.length, 3);
      expect(sumWithPot(s), 0);
    });
  });

  group('Hệ số tuỳ chỉnh', () {
    test('đổi hệ số Ù và cược', () {
      final s = fresh(bet: 20);
      s.settings.uMoiNguoi = 3;
      must(s, buildU(s, 'p1', null));
      expect(money(s, 'p1'), 180);
      expect(money(s, 'p2'), -60);
    });
  });

  group('Hoàn tác', () {
    test('huỷ đúng thao tác cuối, kể cả đóng ván', () {
      final c = GameController(state: fresh());
      c.apply(buildAnChot(c.state, 'p1', 'p2'));
      c.apply(buildU(c.state, 'p3', null));
      expect(c.state.history.length, 1);
      expect(c.undoLabel, contains('Ù'));
      c.undo();
      expect(c.state.history, isEmpty);
      expect(c.state.current.length, 1);
      expect(money(c.state, 'p2'), 40);
      c.undo();
      expect(money(c.state, 'p2'), 0);
      expect(c.canUndo, isFalse);
    });

    test('reset hoàn tác được', () {
      final c = GameController(state: fresh());
      c.apply(buildAnChot(c.state, 'p1', 'p2'));
      c.reset();
      expect(money(c.state, 'p2'), 0);
      c.undo();
      expect(money(c.state, 'p2'), 40);
    });

    test('giữ tối đa 30 bước', () {
      final c = GameController(state: fresh());
      for (var i = 0; i < 40; i++) {
        c.apply(buildAnChot(c.state, 'p1', 'p2'));
      }
      var n = 0;
      while (c.canUndo) {
        c.undo();
        n++;
      }
      expect(n, GameController.maxUndo);
    });
  });

  group('Cài đặt và đổi tên', () {
    test('chặn trùng tên, tên rỗng, cược không hợp lệ', () {
      final c = GameController(state: fresh());
      expect(c.rename('p1', 'Người 2'), isNotNull);
      expect(c.rename('p1', '  '), isNotNull);
      final st = c.state.settings.copy()..bet = 0;
      expect(c.updateSettings(st, {}), isNotNull);
    });

    test('không đổi số người khi ván đang dở', () {
      final c = GameController(state: fresh());
      c.apply(buildNopGa(c.state, 'p1'));
      final st = c.state.settings.copy()..playerCount = 3;
      expect(c.updateSettings(st, {}), contains('Ván đang chơi dở'));
    });
  });

  group('Lưu file', () {
    test('lưu và đọc lại đúng trạng thái, kể cả ngăn hoàn tác', () async {
      final dir = await Directory.systemTemp.createTemp('tala');
      final storage = Storage(dir: () async => dir);
      final c = GameController(state: fresh(), storage: storage);
      c.apply(buildNopGa(c.state, 'p1'));
      c.apply(buildAnCay(c.state, 'p2', 'p3'));
      c.rename('p4', 'Hùng');
      await c.save();
      final c2 = await GameController.load(storage);
      expect(c2.state.pot, 10);
      expect(money(c2.state, 'p3'), 10);
      expect(c2.name('p4'), 'Hùng');
      expect(c2.state.current.length, 2);
      expect(c2.canUndo, isTrue);
      c2.undo();
      expect(c2.name('p4'), 'Người 4');
    });

    test('file hỏng thì khởi tạo mới và giữ bản .bak', () async {
      final dir = await Directory.systemTemp.createTemp('tala');
      File('${dir.path}/tala_data.json').writeAsStringSync('{hỏng');
      final c = await GameController.load(Storage(dir: () async => dir));
      expect(c.state.pot, 0);
      expect(File('${dir.path}/tala_data.json.bak').existsSync(), isTrue);
    });
  });
}
