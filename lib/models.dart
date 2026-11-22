// Mô hình dữ liệu của app. Mọi thứ đều chuyển được sang/từ JSON để lưu file.

const int kMaxPlayers = 4;
const int kMinPlayers = 2;

/// Loại sự kiện trong một ván.
enum EventType { anCay, anChot, nopGa, u, xepHang }

EventType _eventTypeFrom(String s) =>
    EventType.values.firstWhere((e) => e.name == s, orElse: () => EventType.anCay);

/// Hạng của một người chơi khi xếp hạng cuối ván.
enum Hang { nhat, nhi, ba, bet, mom }

const Map<Hang, String> kTenHang = {
  Hang.nhat: 'Nhất',
  Hang.nhi: 'Nhì',
  Hang.ba: 'Ba',
  Hang.bet: 'Bét',
  Hang.mom: 'Móm',
};

class Player {
  final String id;
  String name;
  int money;

  Player({required this.id, required this.name, this.money = 0});

  Map<String, dynamic> toJson() => {'id': id, 'name': name, 'money': money};

  factory Player.fromJson(Map<String, dynamic> j) => Player(
        id: j['id'] as String,
        name: j['name'] as String,
        money: (j['money'] as num).toInt(),
      );

  Player copy() => Player(id: id, name: name, money: money);
}

/// Hệ số tiền, đều tính theo "x mức cược".
class Settings {
  int playerCount;
  int bet; // đơn vị: nghìn đồng (k)
  int uMoiNguoi; // mỗi người phải trả khi có người Ù
  List<int> anCay; // ăn cây lần 1/2/3
  int anChot;
  List<int> nopGa; // nộp gà lần 1/2/3
  List<int> xepHang; // Nhì / Ba / Bét
  int mom;

  Settings({
    this.playerCount = 4,
    this.bet = 10,
    this.uMoiNguoi = 5,
    List<int>? anCay,
    this.anChot = 4,
    List<int>? nopGa,
    List<int>? xepHang,
    this.mom = 4,
  })  : anCay = anCay ?? [1, 2, 4],
        nopGa = nopGa ?? [1, 2, 4],
        xepHang = xepHang ?? [1, 2, 3];

  Map<String, dynamic> toJson() => {
        'playerCount': playerCount,
        'bet': bet,
        'uMoiNguoi': uMoiNguoi,
        'anCay': anCay,
        'anChot': anChot,
        'nopGa': nopGa,
        'xepHang': xepHang,
        'mom': mom,
      };

  static List<int> _list3(dynamic v, List<int> def) {
    if (v is List && v.length == 3) {
      return v.map((e) => (e as num).toInt()).toList();
    }
    return List.of(def);
  }

  factory Settings.fromJson(Map<String, dynamic> j) {
    final d = Settings();
    int i(String k, int def) => (j[k] is num) ? (j[k] as num).toInt() : def;
    return Settings(
      playerCount: i('playerCount', d.playerCount).clamp(kMinPlayers, kMaxPlayers),
      bet: i('bet', d.bet),
      uMoiNguoi: i('uMoiNguoi', d.uMoiNguoi),
      anCay: _list3(j['anCay'], d.anCay),
      anChot: i('anChot', d.anChot),
      nopGa: _list3(j['nopGa'], d.nopGa),
      xepHang: _list3(j['xepHang'], d.xepHang),
      mom: i('mom', d.mom),
    );
  }

  Settings copy() => Settings.fromJson(toJson());
}

/// Một sự kiện tiền trong ván. Lưu theo mã người chơi để đổi tên không ảnh hưởng.
class GameEvent {
  final EventType type;
  final DateTime time;

  /// Người mất tiền (ăn cây, ăn chốt, nộp gà) hoặc người đền làng (Ù).
  final String? loserId;

  /// Người được tiền (ăn cây, ăn chốt) hoặc người Ù / người Nhất.
  final String? winnerId;

  /// Lần thứ mấy (ăn cây, nộp gà).
  final int lan;

  /// Thay đổi tiền của từng người trong sự kiện này.
  final Map<String, int> deltas;

  /// Thay đổi quỹ gà (+ là nộp vào, - là bị ăn).
  final int potDelta;

  /// Hạng từng người (chỉ với xếp hạng).
  final Map<String, Hang> hang;

  GameEvent({
    required this.type,
    required this.time,
    this.loserId,
    this.winnerId,
    this.lan = 0,
    required this.deltas,
    this.potDelta = 0,
    Map<String, Hang>? hang,
  }) : hang = hang ?? const {};

  Map<String, dynamic> toJson() => {
        'type': type.name,
        'time': time.toIso8601String(),
        'loserId': loserId,
        'winnerId': winnerId,
        'lan': lan,
        'deltas': deltas,
        'potDelta': potDelta,
        'hang': hang.map((k, v) => MapEntry(k, v.name)),
      };

  factory GameEvent.fromJson(Map<String, dynamic> j) => GameEvent(
        type: _eventTypeFrom(j['type'] as String),
        time: DateTime.tryParse(j['time'] as String? ?? '') ?? DateTime.now(),
        loserId: j['loserId'] as String?,
        winnerId: j['winnerId'] as String?,
        lan: (j['lan'] as num?)?.toInt() ?? 0,
        deltas: ((j['deltas'] as Map?) ?? {})
            .map((k, v) => MapEntry(k as String, (v as num).toInt())),
        potDelta: (j['potDelta'] as num?)?.toInt() ?? 0,
        hang: ((j['hang'] as Map?) ?? {}).map((k, v) => MapEntry(
            k as String, Hang.values.firstWhere((h) => h.name == v, orElse: () => Hang.bet))),
      );
}

/// Một ván đã kết thúc, nằm trong lịch sử.
class Round {
  final int number;
  final DateTime endedAt;
  final List<GameEvent> events; // sự kiện cuối là Ù hoặc xếp hạng
  final Map<String, int> deltas; // tổng +/- từng người trong ván
  final Map<String, int> totalsAfter; // tổng tích luỹ sau ván
  final List<String> playerIds; // ai chơi ván này

  Round({
    required this.number,
    required this.endedAt,
    required this.events,
    required this.deltas,
    required this.totalsAfter,
    required this.playerIds,
  });

  GameEvent get last => events.last;

  Map<String, dynamic> toJson() => {
        'number': number,
        'endedAt': endedAt.toIso8601String(),
        'events': events.map((e) => e.toJson()).toList(),
        'deltas': deltas,
        'totalsAfter': totalsAfter,
        'playerIds': playerIds,
      };

  factory Round.fromJson(Map<String, dynamic> j) {
    Map<String, int> m(dynamic v) =>
        ((v as Map?) ?? {}).map((k, v) => MapEntry(k as String, (v as num).toInt()));
    return Round(
      number: (j['number'] as num).toInt(),
      endedAt: DateTime.tryParse(j['endedAt'] as String? ?? '') ?? DateTime.now(),
      events: ((j['events'] as List?) ?? [])
          .map((e) => GameEvent.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      deltas: m(j['deltas']),
      totalsAfter: m(j['totalsAfter']),
      playerIds: ((j['playerIds'] as List?) ?? []).cast<String>(),
    );
  }
}

/// Toàn bộ trạng thái của app (trừ ngăn hoàn tác).
class GameState {
  Settings settings;
  List<Player> players; // luôn đủ 4 người, chỉ [playerCount] người đầu đang chơi
  int pot;
  List<GameEvent> current; // sự kiện của ván đang chơi
  List<Round> history; // mới nhất ở đầu

  GameState({
    required this.settings,
    required this.players,
    this.pot = 0,
    List<GameEvent>? current,
    List<Round>? history,
  })  : current = current ?? [],
        history = history ?? [];

  factory GameState.initial() => GameState(
        settings: Settings(),
        players: List.generate(
            kMaxPlayers, (i) => Player(id: 'p${i + 1}', name: 'Người ${i + 1}')),
      );

  List<Player> get active => players.take(settings.playerCount).toList();

  int get roundNumber => (history.isEmpty ? 0 : history.first.number) + 1;

  Player byId(String id) => players.firstWhere((p) => p.id == id);

  String nameOf(String? id) {
    if (id == null) return '?';
    for (final p in players) {
      if (p.id == id) return p.name;
    }
    return '?';
  }

  Map<String, dynamic> toJson() => {
        'settings': settings.toJson(),
        'players': players.map((p) => p.toJson()).toList(),
        'pot': pot,
        'current': current.map((e) => e.toJson()).toList(),
        'history': history.map((r) => r.toJson()).toList(),
      };

  factory GameState.fromJson(Map<String, dynamic> j) {
    final init = GameState.initial();
    final players = ((j['players'] as List?) ?? [])
        .map((e) => Player.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
    // Bảo đảm luôn đủ 4 người với mã p1..p4.
    for (final p in init.players) {
      if (!players.any((x) => x.id == p.id)) players.add(p);
    }
    players.sort((a, b) => a.id.compareTo(b.id));
    return GameState(
      settings: Settings.fromJson(Map<String, dynamic>.from((j['settings'] as Map?) ?? {})),
      players: players.take(kMaxPlayers).toList(),
      pot: (j['pot'] as num?)?.toInt() ?? 0,
      current: ((j['current'] as List?) ?? [])
          .map((e) => GameEvent.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      history: ((j['history'] as List?) ?? [])
          .map((e) => Round.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
    );
  }

  GameState copy() => GameState.fromJson(toJson());
}
