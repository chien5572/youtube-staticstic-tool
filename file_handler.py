"""
file_handler.py — Module xử lý xuất file JSON và CSV.

Các chức năng chính:
- Tạo tên file với versioning tự động
- Lưu dữ liệu ra file JSON theo template
- Convert JSON sang CSV (mỗi row = 1 video + thông tin channel lặp lại)
"""

import os
import re
import json
import csv


def sanitize_channel_name(name):
    """
    Chuẩn hóa tên channel để làm tên file.
    
    Quy tắc:
    - Thay khoảng trắng bằng dấu "-"
    - Bỏ ký tự đặc biệt (chỉ giữ chữ, số, dấu "-")
    - Viết liền, không dấu tiếng Việt vẫn giữ nguyên
    
    Args:
        name: Tên channel gốc
        
    Returns:
        Tên đã chuẩn hóa (string)
    """
    # Thay khoảng trắng bằng dấu "-"
    name = name.strip().replace(" ", "-")
    # Bỏ ký tự đặc biệt, chỉ giữ chữ, số, dấu "-", và ký tự Unicode (tiếng Việt, etc.)
    name = re.sub(r"[^\w\-]", "", name, flags=re.UNICODE)
    # Loại bỏ nhiều dấu "-" liên tiếp
    name = re.sub(r"-{2,}", "-", name)
    # Bỏ dấu "-" ở đầu và cuối
    name = name.strip("-")
    return name if name else "channel"


def generate_filename(channel_name, mode, output_dir, extension=".json"):
    """
    Tạo tên file với versioning tự động.
    
    Quy tắc:
    - Lần đầu: TenKenh_mode.ext
    - Lần 2: TenKenh_mode_v1.ext  
    - Lần 3: TenKenh_mode_v2.ext
    
    Args:
        channel_name: Tên channel đã sanitize
        mode: Chế độ ("all", "100new", "100views")
        output_dir: Thư mục output
        extension: Phần mở rộng file (".json" hoặc ".csv")
        
    Returns:
        Đường dẫn file đầy đủ (string)
    """
    base_name = f"{channel_name}_{mode}"
    filepath = os.path.join(output_dir, f"{base_name}{extension}")

    if not os.path.exists(filepath):
        return filepath

    # Tìm version cao nhất hiện có
    version = 1
    while True:
        filepath = os.path.join(output_dir, f"{base_name}_v{version}{extension}")
        if not os.path.exists(filepath):
            return filepath
        version += 1


def generate_file_pair(channel_name, mode, output_dir):
    """
    Tạo cặp tên file JSON và CSV với cùng version.
    
    File JSON được lưu vào output_dir/json/
    File CSV được lưu vào output_dir/csv/
    
    Args:
        channel_name: Tên channel gốc (chưa sanitize)
        mode: Chế độ ("all", "100new", "100views")
        output_dir: Thư mục output gốc
        
    Returns:
        Tuple (json_path, csv_path)
    """
    sanitized_name = sanitize_channel_name(channel_name)
    base_name = f"{sanitized_name}_{mode}"

    # Tạo subfolder json/ và csv/
    json_dir = os.path.join(output_dir, "json")
    csv_dir = os.path.join(output_dir, "csv")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    # Kiểm tra cả 2 file cùng lúc để đảm bảo cùng version
    json_path = os.path.join(json_dir, f"{base_name}.json")
    csv_path = os.path.join(csv_dir, f"{base_name}.csv")

    if not os.path.exists(json_path) and not os.path.exists(csv_path):
        return json_path, csv_path

    version = 1
    while True:
        json_path = os.path.join(json_dir, f"{base_name}_v{version}.json")
        csv_path = os.path.join(csv_dir, f"{base_name}_v{version}.csv")
        if not os.path.exists(json_path) and not os.path.exists(csv_path):
            return json_path, csv_path
        version += 1


def save_json(data, filepath):
    """
    Lưu dữ liệu ra file JSON theo template.
    
    Format output:
    {
        "channel_name": "...",
        "channel_link": "...",
        "subcriber": "...",
        "video_num": "...",
        "videos_list": [
            {
                "title": "...",
                "view_count": "...",
                "published_at": "dd/MM/yyyy",
                "duration": "giây",
                "video_link": "..."
            }
        ]
    }
    
    Args:
        data: Dict chứa dữ liệu theo format template
        filepath: Đường dẫn file output
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def convert_json_to_csv(json_filepath, csv_filepath):
    """
    Convert file JSON sang CSV.
    
    Mỗi row trong CSV = 1 video, kèm thông tin channel lặp lại.
    Cột "videos_list" để trống.
    
    Header: channel_name, channel_link, subcriber, video_num, videos_list,
            title, view_count, published_at, duration, video_link
    
    Args:
        json_filepath: Đường dẫn file JSON input
        csv_filepath: Đường dẫn file CSV output
    """
    with open(json_filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    channel_name = data.get("channel_name", "")
    channel_link = data.get("channel_link", "")
    subcriber = data.get("subcriber", "")
    video_num = data.get("video_num", "")
    videos = data.get("videos_list", [])

    headers = [
        "channel_name", "channel_link", "subcriber", "video_num",
        "videos_list", "title", "view_count", "published_at", "duration", "video_link"
    ]

    with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        for video in videos:
            row = [
                channel_name,
                channel_link,
                subcriber,
                video_num,
                "",  # videos_list - để trống
                video.get("title", ""),
                video.get("view_count", ""),
                video.get("published_at", ""),
                video.get("duration", ""),
                video.get("video_link", "")
            ]
            writer.writerow(row)


def build_output_data(channel_info, videos_list):
    """
    Xây dựng dữ liệu output theo format template.
    
    Args:
        channel_info: Dict chứa thông tin channel
        videos_list: List các video dict
        
    Returns:
        Dict theo format template JSON
    """
    return {
        "channel_name": channel_info.get("channel_name", ""),
        "channel_link": channel_info.get("channel_link", ""),
        "subcriber": channel_info.get("subcriber", "0"),
        "video_num": channel_info.get("video_num", "0"),
        "videos_list": videos_list
    }
