# 📊 YouTube Statistic Tool

Ứng dụng desktop Python giúp lấy dữ liệu thống kê video từ kênh YouTube thông qua YouTube Data API v3. Xuất kết quả ra file JSON và CSV.

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Hướng dẫn lấy YouTube API Key](#-hướng-dẫn-lấy-youtube-api-key)
- [Cài đặt](#-cài-đặt)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
- [Định dạng output](#-định-dạng-output)
- [Giới hạn và lưu ý](#-giới-hạn-và-lưu-ý)

---

## ✨ Tính năng

| Chức năng | Mô tả |
|---|---|
| **All** | Lấy toàn bộ video mới nhất từ kênh (tối đa 1000 video) |
| **100new** | Lấy 100 video mới nhất |
| **100views** | Lấy 100 video có lượt xem cao nhất |

**Thông tin được thu thập cho mỗi video:**
- Tiêu đề video
- Lượt xem
- Ngày đăng (dd/MM/yyyy)
- Thời lượng (quy đổi sang giây)
- Link video

**Thông tin kênh:**
- Tên kênh
- Link kênh
- Số lượng subscriber
- Tổng số video

---

## 💻 Yêu cầu hệ thống

- **Python**: 3.7 trở lên
- **Hệ điều hành**: Windows / macOS / Linux
- **Kết nối mạng**: Cần có internet để gọi YouTube API

---

## 🔑 Hướng dẫn lấy YouTube API Key

Để sử dụng ứng dụng, bạn cần một YouTube Data API v3 Key (miễn phí). Thực hiện theo các bước sau:

### Bước 1: Truy cập Google Cloud Console

1. Mở trình duyệt và truy cập: [https://console.cloud.google.com](https://console.cloud.google.com)
2. Đăng nhập bằng tài khoản Google của bạn

### Bước 2: Tạo Project mới

1. Click vào dropdown **"Select a project"** ở thanh trên cùng
2. Click **"NEW PROJECT"**
3. Nhập tên project (ví dụ: `YouTube Statistic`)
4. Click **"CREATE"**
5. Đợi vài giây để project được tạo xong, sau đó chọn project vừa tạo

### Bước 3: Bật YouTube Data API v3

1. Vào menu bên trái, chọn **"APIs & Services"** → **"Library"**
2. Trong ô tìm kiếm, gõ **"YouTube Data API v3"**
3. Click vào kết quả **"YouTube Data API v3"**
4. Click nút **"ENABLE"** để bật API

### Bước 4: Tạo API Key

1. Vào menu bên trái, chọn **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. Một API key mới sẽ được tạo và hiển thị trên màn hình
4. **Copy API key** này và dán vào ứng dụng

> ⚠️ **Lưu ý bảo mật**: Không chia sẻ API key với người khác. Bạn có thể giới hạn API key chỉ hoạt động với YouTube Data API v3 trong phần **"Restrict key"**.

### Bước 5 (Tùy chọn): Giới hạn API Key

1. Click vào tên API key vừa tạo
2. Trong phần **"API restrictions"**, chọn **"Restrict key"**
3. Chọn **"YouTube Data API v3"** từ dropdown
4. Click **"Save"**

---

## 🛠 Cài đặt

### 1. Cài đặt Python

Nếu chưa có Python, tải và cài đặt từ: [https://www.python.org/downloads/](https://www.python.org/downloads/)

> Khi cài đặt, nhớ tick ✅ **"Add Python to PATH"**

### 2. Cài đặt thư viện

Mở Terminal/Command Prompt và chạy:

```bash
pip install requests
```

### 3. Tải source code

Tải hoặc clone source code về máy.

---

## 🚀 Hướng dẫn sử dụng

### Khởi chạy ứng dụng

```bash
cd youtube-statistic
python main.py
```

### Các bước sử dụng

1. **Nhập API Key**: Dán YouTube API Key vào ô đầu tiên. Key sẽ được lưu lại để dùng cho lần sau.

2. **Nhập link channel**: Dán link kênh YouTube vào ô thứ hai. Hỗ trợ các định dạng:
   - `https://www.youtube.com/@TenKenh`
   - `https://www.youtube.com/channel/UCxxxxxx`
   - `https://www.youtube.com/c/TenKenh`
   - `https://www.youtube.com/user/TenKenh`

3. **Chọn thư mục output**: Click **"Chọn..."** để chọn thư mục lưu file kết quả.

4. **Chọn chức năng**:
   - 📋 **Tất cả video** (tối đa 1000)
   - 🆕 **100 video mới nhất**
   - 🔥 **100 video nhiều lượt xem nhất**

5. **Bấm "BẮT ĐẦU LẤY DỮ LIỆU"** và chờ đợi. Thanh tiến trình sẽ hiển thị trạng thái.

6. Khi hoàn tất, các file kết quả sẽ được tự động phân loại và lưu vào các thư mục con trong thư mục output đã chọn:
   - Thư mục `json/` chứa file: `TenKenh_chucNang.json`
   - Thư mục `csv/` chứa file: `TenKenh_chucNang.csv`

---

## 📁 Định dạng output

### File JSON

```json
{
    "channel_name": "Tên kênh",
    "channel_link": "https://www.youtube.com/channel/UCxxxxxx",
    "subcriber": "1000000",
    "video_num": "500",
    "videos_list": [
        {
            "title": "Tiêu đề video",
            "view_count": "50000",
            "published_at": "15/01/2025",
            "duration": "300",
            "video_link": "https://www.youtube.com/watch?v=xxxxxx"
        }
    ]
}
```

### File CSV

| channel_name | channel_link | subcriber | video_num | videos_list | title | view_count | published_at | duration | video_link |
|---|---|---|---|---|---|---|---|---|---|
| Tên kênh | link | 1000000 | 500 | | Video 1 | 50000 | 15/01/2025 | 300 | link |

> Cột `videos_list` để trống trong CSV vì dữ liệu video đã được flatten ra các cột riêng.

### Quy tắc đặt tên và lưu trữ file

- Cấu trúc lưu trữ:
  ```
  📁 thư-mục-output/
  ├── 📁 json/
  │   └── TenKenh_chucNang.json
  └── 📁 csv/
      └── TenKenh_chucNang.csv
  ```
- Khoảng trắng trong tên kênh được thay bằng dấu `-`.
- Nếu file đã tồn tại: hệ thống tự động thêm `_v1`, `_v2`... ở cuối tên để tránh ghi đè dữ liệu cũ.

```
Lần 1: json/Tech-Channel_all.json và csv/Tech-Channel_all.csv
Lần 2: json/Tech-Channel_all_v1.json và csv/Tech-Channel_all_v1.csv
Lần 3: json/Tech-Channel_all_v2.json và csv/Tech-Channel_all_v2.csv
```

---

## ⚠️ Giới hạn và lưu ý

### Giới hạn API Quota

YouTube Data API v3 miễn phí giới hạn **10,000 quota/ngày**.

| Chức năng | Quota ước tính | Số lần chạy/ngày |
|---|---|---|
| All (1000 video) | ~43 quota | ~230 lần |
| 100new | ~6 quota | ~1600 lần |
| 100views | ~43 quota | ~230 lần |

> Ứng dụng sử dụng `playlistItems` API (1 quota/request) thay vì `search` API (100 quota/request), giúp tiết kiệm quota đáng kể.

> Quota được reset vào **00:00 giờ Pacific Time** (khoảng 14:00 giờ Việt Nam).

### Xử lý lỗi

Ứng dụng sẽ hiển thị thông báo popup khi gặp lỗi:
- ❌ API key không hợp lệ
- ❌ Link channel không đúng
- ❌ Hết quota API
- ❌ Mất kết nối mạng

---

## 📄 Cấu trúc project

```
youtube-statistic/
├── main.py              # Giao diện chính (GUI)
├── youtube_api.py       # Module gọi YouTube API
├── file_handler.py      # Module xuất file JSON/CSV
├── config.json          # Lưu API key (tự động tạo, được bỏ qua bởi .gitignore)
├── .gitignore           # Cấu hình bỏ qua các file nhạy cảm và file tạm khi push Git
├── output_json_template.json
├── output_csv_template.csv
└── README.md            # File hướng dẫn này
```

---

## 📝 License

Dự án này được tạo cho mục đích cá nhân và học tập.
