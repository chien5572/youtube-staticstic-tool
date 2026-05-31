# YouTube Statistic App — Walkthrough

## Tổng quan

Đã xây dựng hoàn chỉnh ứng dụng desktop Python để lấy dữ liệu thống kê video từ kênh YouTube thông qua YouTube Data API v3.

---

## Các file đã tạo

### 1. [youtube_api.py](file:///d:/workspace/vibe-code-app/youtube-statistic/youtube_api.py)

Module core xử lý tương tác với YouTube Data API v3:

| Hàm | Chức năng |
|---|---|
| `validate_api_key()` | Kiểm tra API key hợp lệ |
| `extract_channel_id()` | Trích xuất Channel ID từ nhiều dạng URL (`/@handle`, `/channel/`, `/c/`, `/user/`) |
| `get_channel_info()` | Lấy thông tin kênh (tên, subscriber, tổng video) |
| `get_all_videos()` | Lấy tất cả video (max 1000), progress callback |
| `get_latest_100()` | Lấy 100 video mới nhất |
| `get_top_100_views()` | Lấy top 100 video view cao nhất (fetch 500 → sort → top 100) |
| `get_video_details()` | Batch lấy chi tiết video (50/request) |

**Custom exceptions**: `YouTubeAPIError`, `QuotaExceededError`, `InvalidAPIKeyError`, `ChannelNotFoundError`

---

### 2. [file_handler.py](file:///d:/workspace/vibe-code-app/youtube-statistic/file_handler.py)

Module xử lý xuất file:

| Hàm | Chức năng |
|---|---|
| `sanitize_channel_name()` | Chuẩn hóa tên kênh (thay space → `-`, bỏ ký tự đặc biệt) |
| `generate_file_pair()` | Tạo cặp tên file JSON+CSV cùng version |
| `save_json()` | Lưu JSON theo template |
| `convert_json_to_csv()` | Convert JSON → CSV (mỗi row = 1 video + channel info lặp lại) |
| `build_output_data()` | Xây dựng data theo format template |

**Versioning**: `file.json` → `file_v1.json` → `file_v2.json`

---

### 3. [main.py](file:///d:/workspace/vibe-code-app/youtube-statistic/main.py)

GUI Tkinter — giao diện chính của ứng dụng:

- **Light mode** với color palette curated (xanh dương primary `#2563EB`)
- **Tiếng Việt** toàn bộ giao diện
- **API Key**: Nhập + toggle hiện/ẩn + lưu vào `config.json`
- **Channel URL**: Validate trước khi gọi API
- **Output folder**: Chọn bằng file dialog
- **3 Radio buttons**: All / 100new / 100views
- **Progress bar**: Cập nhật real-time qua `root.after()`
- **Threading**: API calls chạy trên background thread → GUI responsive

---

### 4. [README.md](file:///d:/workspace/vibe-code-app/youtube-statistic/README.md)

Tài liệu hướng dẫn đầy đủ:

- Giới thiệu ứng dụng & tính năng
- **Hướng dẫn lấy YouTube API Key** (5 bước chi tiết)
- Cài đặt & khởi chạy
- Hướng dẫn sử dụng từng bước
- Định dạng output JSON & CSV
- Bảng quota API & giới hạn

---

## Thư viện sử dụng

| Thư viện | Nguồn | Mục đích |
|---|---|---|
| `tkinter` | Có sẵn Python | GUI |
| `tkinter.ttk` | Có sẵn Python | Styled widgets |
| `requests` | `pip install` | HTTP requests to YouTube API |
| `json`, `csv`, `re`, `os`, `threading` | Có sẵn Python | Utilities |

---

## Verification

| Kiểm tra | Kết quả |
|---|---|
| Import tất cả modules | ✅ Passed |
| Khởi chạy GUI | ✅ App mở thành công |
| `requests` installed | ✅ v2.34.2 |

---

## Cách test với dữ liệu thật

1. Chạy `python main.py`
2. Nhập YouTube API Key
3. Nhập link channel (VD: `https://www.youtube.com/@Google`)
4. Chọn thư mục output
5. Chọn chức năng "100 video mới nhất" (tốn ít quota nhất)
6. Bấm "BẮT ĐẦU LẤY DỮ LIỆU"
7. Kiểm tra file JSON và CSV trong thư mục output
