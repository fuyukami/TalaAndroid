import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tala_pro/controller.dart';
import 'package:tala_pro/main.dart';
import 'package:tala_pro/models.dart';

Future<GameController> pumpApp(WidgetTester tester, {GameState? state}) async {
  tester.view.physicalSize = const Size(1170, 2532);
  tester.view.devicePixelRatio = 3;
  addTearDown(tester.view.reset);
  final c = GameController(state: state ?? GameState.initial());
  await tester.pumpWidget(TalaApp(controller: c));
  await tester.pumpAndSettle();
  return c;
}

Future<void> tapText(WidgetTester tester, String text, {int index = 0}) async {
  final f = find.text(text);
  if (f.evaluate().length <= index) {
    await tester.scrollUntilVisible(f, 300, scrollable: find.byType(Scrollable).first);
  }
  await tester.ensureVisible(f.at(index));
  await tester.pumpAndSettle();
  await tester.tap(f.at(index));
  await tester.pumpAndSettle();
}

bool onHome(WidgetTester tester) =>
    !tester.state<NavigatorState>(find.byType(Navigator)).canPop();

Future<void> systemBack(WidgetTester tester) async {
  await tester.binding.handlePopRoute();
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('Ăn cây qua giao diện', (tester) async {
    final c = await pumpApp(tester);
    await tapText(tester, 'ĂN CÂY');
    await tapText(tester, 'Người 1');
    await tapText(tester, 'Người 2', index: 1);
    await tapText(tester, 'XÁC NHẬN');
    expect(c.state.byId('p1').money, -10);
    expect(c.state.byId('p2').money, 10);
    expect(onHome(tester), isTrue);
  });

  testWidgets('Vuốt quay lại giữa lúc xử lý Ù không làm treo app', (tester) async {
    final c = await pumpApp(tester);
    await tapText(tester, 'XỬ LÝ Ù');
    await tapText(tester, 'Người 2');
    await systemBack(tester);
    expect(onHome(tester), isTrue);
    expect(c.state.byId('p2').money, 0);

    // Các menu khác vẫn bấm được sau khi vuốt quay lại.
    await tapText(tester, 'XỬ LÝ Ù');
    await tapText(tester, 'Người 2');
    await tapText(tester, 'Không ai đền');
    await tapText(tester, 'XÁC NHẬN');
    // Màn mừng Ù hiện lên, chạm để đóng.
    expect(find.text('Ù!'), findsOneWidget);
    await tester.tap(find.text('Ù!'));
    await tester.pumpAndSettle();
    expect(c.state.byId('p2').money, 150);
    expect(c.state.history.length, 1);

    await tapText(tester, 'ĂN CHỐT');
    await systemBack(tester);
    await tapText(tester, 'Lịch sử');
    expect(find.text('Ván 1 · Người 2 Ù'), findsOneWidget);
    await systemBack(tester);
    await tapText(tester, 'Cài đặt');
    await systemBack(tester);
    expect(onHome(tester), isTrue);
  });

  testWidgets('Xếp hạng và hoàn tác', (tester) async {
    final c = await pumpApp(tester);
    await tapText(tester, 'XẾP HẠNG & KẾT THÚC VÁN');
    await tapText(tester, 'Nhất', index: 3); // Người 4 Nhất
    await tapText(tester, 'Nhì', index: 0); // Người 1 Nhì
    await tapText(tester, 'Ba', index: 1); // Người 2 Ba → Người 3 tự điền Bét
    await tapText(tester, 'KẾT THÚC VÁN');
    expect(c.state.byId('p4').money, 60);
    expect(c.state.byId('p3').money, -30);
    await tapText(tester, 'HOÀN TÁC');
    expect(c.state.byId('p4').money, 0);
    expect(c.state.history, isEmpty);
  });

  testWidgets('Cài đặt: 3 người, đổi hệ số Ù', (tester) async {
    final c = await pumpApp(tester);
    await tapText(tester, 'Cài đặt');
    await tapText(tester, '3 người');
    await tapText(tester, 'LƯU CÀI ĐẶT');
    expect(c.state.settings.playerCount, 3);
    expect(find.text('Người 4'), findsNothing);
    await tapText(tester, 'XỬ LÝ Ù');
    await tapText(tester, 'Người 1');
    await tapText(tester, 'Không ai đền');
    await tapText(tester, 'XÁC NHẬN');
    expect(c.state.byId('p1').money, 100);
    // Màn mừng Ù tự đóng sau vài giây.
    await tester.pump(const Duration(seconds: 4));
    await tester.pumpAndSettle();
    expect(onHome(tester), isTrue);
  });

  testWidgets('Nộp gà tối đa 3 lần thì không chọn được nữa', (tester) async {
    final c = await pumpApp(tester);
    for (var i = 0; i < 3; i++) {
      await tapText(tester, 'NỘP GÀ');
      await tapText(tester, 'Người 3');
      await tapText(tester, 'XÁC NHẬN');
    }
    expect(c.state.pot, 70);
    await tapText(tester, 'NỘP GÀ');
    expect(find.text('đã nộp 3 lần'), findsOneWidget);
  });
}
