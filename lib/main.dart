import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'controller.dart';
import 'storage.dart';
import 'ui/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  final controller = await GameController.load(Storage());
  runApp(TalaApp(controller: controller));
}

/// Cho mọi màn hình truy cập controller và tự vẽ lại khi dữ liệu đổi.
class Ctl extends InheritedNotifier<GameController> {
  const Ctl({super.key, required GameController controller, required super.child})
      : super(notifier: controller);

  static GameController of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<Ctl>()!.notifier!;

  static GameController read(BuildContext context) =>
      context.getInheritedWidgetOfExactType<Ctl>()!.notifier!;
}

class TalaApp extends StatefulWidget {
  final GameController controller;
  const TalaApp({super.key, required this.controller});

  @override
  State<TalaApp> createState() => _TalaAppState();
}

class _TalaAppState extends State<TalaApp> {
  late final AppLifecycleListener _life;

  @override
  void initState() {
    super.initState();
    // Lưu thêm một lần khi app bị đưa xuống nền (Android có thể kill app bất cứ lúc nào).
    _life = AppLifecycleListener(
      onHide: widget.controller.save,
      onPause: widget.controller.save,
      onDetach: widget.controller.save,
    );
  }

  @override
  void dispose() {
    _life.dispose();
    super.dispose();
  }

  ThemeData _theme(Brightness b) {
    final base = ThemeData(
      useMaterial3: true,
      brightness: b,
      fontFamily: 'BeVietnamPro',
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF17694F), brightness: b),
    );
    return base.copyWith(
      pageTransitionsTheme: const PageTransitionsTheme(builders: {
        TargetPlatform.android: FadeForwardsPageTransitionsBuilder(),
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Ctl(
      controller: widget.controller,
      child: MaterialApp(
        title: 'Tá lả Pro',
        debugShowCheckedModeBanner: false,
        theme: _theme(Brightness.light),
        darkTheme: _theme(Brightness.dark),
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
      ),
    );
  }
}
