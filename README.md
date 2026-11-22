# Tá lả Pro

App Android tính điểm tá lả, viết bằng Flutter.

## Tính năng

- Ăn cây, ăn chốt, nộp gà, xử lý Ù (có đền làng), xếp hạng cuối ván. Mỗi thao tác là một màn, xem trước tiền rồi mới xác nhận.
- Chơi 2, 3 hoặc 4 người. Mức cược và toàn bộ hệ số tiền chỉnh được trong Cài đặt.
- Tự lưu sau mỗi thao tác, tắt app mở lại vẫn còn nguyên.
- Hoàn tác 30 bước gần nhất (kể cả Reset).
- Theo dõi diễn biến ván đang chơi, lịch sử từng ván có tiền +/- và tổng tích luỹ của mỗi người.

## Luật tính tiền mặc định (× mức cược)

| Việc | Hệ số |
|---|---|
| Ù, mỗi người trả | 5 (người Ù nhận 5 × số người phải trả, cộng quỹ gà) |
| Đền làng | Một người trả thay cả làng |
| Ăn cây lần 1 / 2 / 3 | 1 / 2 / 4 |
| Ăn chốt | 4 |
| Nộp gà lần 1 / 2 / 3 | 1 / 2 / 4 |
| Nhì / Ba / Bét | 1 / 2 / 3 |
| Móm | 4 |

## Phát triển

Phiên bản dùng chung cho máy phát triển và GitHub Actions: Flutter 3.50.1 (Dart 3.14), JDK 25,
Android Gradle Plugin 9.3.1, Gradle 9.5.0, Kotlin 2.4.20. Các bản Android SDK (compileSdk, targetSdk,
NDK) lấy theo mặc định của Flutter 3.50.1 nên tự khớp.

```
flutter pub get
flutter test      # test luật tính tiền và các luồng giao diện
flutter build apk --release
```

Cấu trúc:

- `lib/models.dart`: dữ liệu (người chơi, sự kiện, ván, cài đặt).
- `lib/rules.dart`: luật tính tiền, thuần Dart.
- `lib/controller.dart`: trạng thái app, hoàn tác, lưu file.
- `lib/storage.dart`: ghi file JSON an toàn.
- `lib/ui/`: các màn hình.

GitHub Actions build APK mỗi lần push lên `main` hoặc mở PR (tải ở mục Artifacts của lượt chạy).

## Khoá ký APK

Để các bản sau cài đè được bản trước (không phải gỡ app, không mất dữ liệu), thêm 4 secret trong
**Settings › Secrets and variables › Actions**: `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`,
`KEY_PASSWORD`. Thiếu secret thì APK được ký bằng khoá debug.

Font Be Vietnam Pro theo giấy phép SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
