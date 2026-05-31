"""
youtube_api.py — Module xử lý tương tác với YouTube Data API v3.

Sử dụng playlistItems.list (Uploads playlist) thay vì search.list
để đảm bảo lấy được ĐẦY ĐỦ video từ channel.

Các chức năng chính:
- Validate API key
- Trích xuất Channel ID từ URL
- Lấy thông tin channel (tên, subscriber, số video, uploads playlist ID)
- Lấy danh sách video theo 3 chế độ: All, 100new, 100views
- Lấy chi tiết video (view count, duration)
"""

import re
import requests
from datetime import datetime

BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(Exception):
    """Custom exception cho các lỗi YouTube API."""
    pass


class QuotaExceededError(YouTubeAPIError):
    """Lỗi khi quota API đã hết."""
    pass


class InvalidAPIKeyError(YouTubeAPIError):
    """Lỗi khi API key không hợp lệ."""
    pass


class ChannelNotFoundError(YouTubeAPIError):
    """Lỗi khi không tìm thấy channel."""
    pass


def _check_api_response(response):
    """Kiểm tra response từ API và raise exception nếu có lỗi."""
    if response.status_code == 200:
        return response.json()

    try:
        error_data = response.json()
        error_info = error_data.get("error", {})
        errors = error_info.get("errors", [])

        if response.status_code == 403:
            for err in errors:
                if err.get("reason") == "quotaExceeded":
                    raise QuotaExceededError(
                        "Quota API đã hết! Giới hạn miễn phí là 10,000 quota/ngày. "
                        "Vui lòng thử lại vào ngày mai hoặc sử dụng API key khác."
                    )
            raise InvalidAPIKeyError(
                "API key không hợp lệ hoặc không có quyền truy cập YouTube Data API v3. "
                "Vui lòng kiểm tra lại API key."
            )

        if response.status_code == 400:
            raise YouTubeAPIError(
                f"Yêu cầu không hợp lệ: {error_info.get('message', 'Lỗi không xác định')}"
            )

        raise YouTubeAPIError(
            f"Lỗi API (HTTP {response.status_code}): {error_info.get('message', 'Lỗi không xác định')}"
        )

    except (ValueError, KeyError):
        raise YouTubeAPIError(f"Lỗi API (HTTP {response.status_code}): Không thể đọc phản hồi từ server.")


def validate_api_key(api_key):
    """
    Kiểm tra API key có hợp lệ không bằng cách gọi thử API.

    Args:
        api_key: YouTube Data API v3 key

    Returns:
        True nếu key hợp lệ

    Raises:
        InvalidAPIKeyError: Nếu key không hợp lệ
        QuotaExceededError: Nếu quota đã hết
        YouTubeAPIError: Các lỗi khác
    """
    try:
        response = requests.get(
            f"{BASE_URL}/channels",
            params={
                "part": "id",
                "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",  # Google Developers channel
                "key": api_key
            },
            timeout=10
        )
        _check_api_response(response)
        return True
    except requests.ConnectionError:
        raise YouTubeAPIError("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.")
    except requests.Timeout:
        raise YouTubeAPIError("Kết nối bị timeout. Vui lòng thử lại.")


def extract_channel_id(channel_url, api_key):
    """
    Trích xuất Channel ID từ URL YouTube.

    Hỗ trợ các dạng URL:
    - https://www.youtube.com/channel/UCxxxxxx
    - https://www.youtube.com/@handle
    - https://www.youtube.com/c/ChannelName
    - https://www.youtube.com/user/Username

    Args:
        channel_url: URL của channel YouTube
        api_key: YouTube API key

    Returns:
        Channel ID (string)

    Raises:
        ChannelNotFoundError: Nếu không tìm thấy channel
        YouTubeAPIError: Nếu URL không hợp lệ
    """
    channel_url = channel_url.strip()

    # Dạng /channel/UCxxxxxx
    match = re.search(r"youtube\.com/channel/(UC[\w-]+)", channel_url)
    if match:
        return match.group(1)

    # Dạng /@handle
    match = re.search(r"youtube\.com/@([\w.-]+)", channel_url)
    if match:
        handle = match.group(1)
        return _resolve_channel_by_handle(handle, api_key)

    # Dạng /c/ChannelName hoặc /user/Username
    match = re.search(r"youtube\.com/(?:c|user)/([\w.-]+)", channel_url)
    if match:
        username = match.group(1)
        return _resolve_channel_by_username(username, api_key)

    # Thử trực tiếp nếu chỉ là handle không có @
    match = re.search(r"youtube\.com/([\w.-]+)$", channel_url)
    if match:
        name = match.group(1)
        # Loại bỏ các path chuẩn
        if name not in ("feed", "watch", "playlist", "results", "shorts", "trending"):
            return _resolve_channel_by_handle(name, api_key)

    raise YouTubeAPIError(
        "Link channel không hợp lệ. Vui lòng nhập đúng định dạng:\n"
        "• https://www.youtube.com/@handle\n"
        "• https://www.youtube.com/channel/UCxxxxxx"
    )


def _resolve_channel_by_handle(handle, api_key):
    """Tìm Channel ID từ handle (@username)."""
    try:
        # Thử dùng forHandle parameter (API mới)
        response = requests.get(
            f"{BASE_URL}/channels",
            params={
                "part": "id",
                "forHandle": handle,
                "key": api_key
            },
            timeout=10
        )
        data = _check_api_response(response)
        items = data.get("items", [])
        if items:
            return items[0]["id"]

        # Fallback: tìm bằng search
        response = requests.get(
            f"{BASE_URL}/search",
            params={
                "part": "snippet",
                "q": handle,
                "type": "channel",
                "maxResults": 1,
                "key": api_key
            },
            timeout=10
        )
        data = _check_api_response(response)
        items = data.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]

        raise ChannelNotFoundError(f"Không tìm thấy channel với handle: @{handle}")

    except requests.ConnectionError:
        raise YouTubeAPIError("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.")
    except requests.Timeout:
        raise YouTubeAPIError("Kết nối bị timeout. Vui lòng thử lại.")


def _resolve_channel_by_username(username, api_key):
    """Tìm Channel ID từ username."""
    try:
        response = requests.get(
            f"{BASE_URL}/channels",
            params={
                "part": "id",
                "forUsername": username,
                "key": api_key
            },
            timeout=10
        )
        data = _check_api_response(response)
        items = data.get("items", [])
        if items:
            return items[0]["id"]

        # Fallback: thử resolve bằng handle
        return _resolve_channel_by_handle(username, api_key)

    except ChannelNotFoundError:
        raise ChannelNotFoundError(f"Không tìm thấy channel với username: {username}")
    except requests.ConnectionError:
        raise YouTubeAPIError("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.")
    except requests.Timeout:
        raise YouTubeAPIError("Kết nối bị timeout. Vui lòng thử lại.")


def get_channel_info(api_key, channel_id):
    """
    Lấy thông tin channel + uploads playlist ID.

    Args:
        api_key: YouTube API key
        channel_id: ID của channel

    Returns:
        dict với keys: channel_name, channel_link, subcriber, video_num, uploads_playlist_id
    """
    try:
        response = requests.get(
            f"{BASE_URL}/channels",
            params={
                "part": "snippet,statistics,contentDetails",
                "id": channel_id,
                "key": api_key
            },
            timeout=10
        )
        data = _check_api_response(response)
        items = data.get("items", [])

        if not items:
            raise ChannelNotFoundError(f"Không tìm thấy channel với ID: {channel_id}")

        channel = items[0]
        snippet = channel["snippet"]
        statistics = channel["statistics"]
        content_details = channel.get("contentDetails", {})

        # Lấy uploads playlist ID (quan trọng!)
        uploads_playlist_id = content_details.get("relatedPlaylists", {}).get("uploads", "")
        if not uploads_playlist_id:
            # Fallback: tạo từ channel ID (UC... -> UU...)
            uploads_playlist_id = "UU" + channel_id[2:]

        return {
            "channel_name": snippet["title"],
            "channel_link": f"https://www.youtube.com/channel/{channel_id}",
            "subcriber": statistics.get("subscriberCount", "0"),
            "video_num": statistics.get("videoCount", "0"),
            "uploads_playlist_id": uploads_playlist_id
        }

    except requests.ConnectionError:
        raise YouTubeAPIError("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.")
    except requests.Timeout:
        raise YouTubeAPIError("Kết nối bị timeout. Vui lòng thử lại.")


def _parse_duration_to_seconds(duration_str):
    """
    Chuyển đổi duration ISO 8601 (PT1H2M3S) sang giây.

    Args:
        duration_str: Chuỗi duration ISO 8601 (VD: "PT1H2M30S")

    Returns:
        Số giây (int)
    """
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def _format_date(date_str):
    """
    Chuyển đổi datetime ISO 8601 sang định dạng dd/MM/yyyy.

    Args:
        date_str: Chuỗi datetime ISO 8601 (VD: "2025-01-15T10:30:00Z")

    Returns:
        Chuỗi ngày dd/MM/yyyy
    """
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return date_str


def get_video_details(api_key, video_ids, progress_callback=None):
    """
    Lấy chi tiết video (view count, duration, title, publishedAt) — batch 50 video/request.

    Args:
        api_key: YouTube API key
        video_ids: List các video ID
        progress_callback: Hàm callback(fetched_count, total_count) tùy chọn

    Returns:
        dict mapping video_id -> {view_count, duration, title, published_at}
    """
    details = {}
    batch_size = 50
    total = len(video_ids)

    for i in range(0, total, batch_size):
        batch = video_ids[i:i + batch_size]
        try:
            response = requests.get(
                f"{BASE_URL}/videos",
                params={
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(batch),
                    "key": api_key
                },
                timeout=15
            )
            data = _check_api_response(response)

            for item in data.get("items", []):
                vid = item["id"]
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                details[vid] = {
                    "title": snippet.get("title", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "view_count": stats.get("viewCount", "0"),
                    "duration": str(_parse_duration_to_seconds(content.get("duration", "PT0S")))
                }

        except requests.ConnectionError:
            raise YouTubeAPIError("Mất kết nối mạng khi lấy chi tiết video.")
        except requests.Timeout:
            raise YouTubeAPIError("Kết nối bị timeout khi lấy chi tiết video.")

        if progress_callback:
            progress_callback(min(i + batch_size, total), total)

    return details


def _fetch_video_ids_from_playlist(api_key, playlist_id, max_results, progress_callback=None):
    """
    Lấy danh sách video ID từ playlist (Uploads playlist) bằng playlistItems API.
    
    Ưu điểm so với search API:
    - Trả về ĐẦY ĐỦ tất cả video
    - Chỉ tốn 1 quota/request (thay vì 100 cho search)
    - Kết quả theo thứ tự mới nhất trước
    
    Args:
        api_key: YouTube API key
        playlist_id: ID của playlist (uploads playlist)
        max_results: Số lượng video tối đa cần lấy
        progress_callback: Hàm callback(current, total, status_text)
        
    Returns:
        List các video ID (string)
    """
    video_ids = []
    next_page_token = None
    total_fetched = 0

    while total_fetched < max_results:
        per_page = min(50, max_results - total_fetched)
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": per_page,
            "key": api_key
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = requests.get(f"{BASE_URL}/playlistItems", params=params, timeout=15)
            data = _check_api_response(response)
        except requests.ConnectionError:
            raise YouTubeAPIError("Mất kết nối mạng khi lấy danh sách video.")
        except requests.Timeout:
            raise YouTubeAPIError("Kết nối bị timeout khi lấy danh sách video.")

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)
                total_fetched += 1

                if total_fetched >= max_results:
                    break

        if progress_callback:
            progress_callback(total_fetched, max_results,
                              f"Đang lấy danh sách video: {total_fetched}/{max_results}...")

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def _build_video_list(api_key, video_ids, progress_callback=None, progress_phase1_pct=50):
    """
    Lấy chi tiết video và xây dựng list kết quả theo format template.
    
    Args:
        api_key: YouTube API key
        video_ids: List video ID
        progress_callback: Hàm callback(current, total, status_text)
        progress_phase1_pct: Phần trăm progress đã hoàn thành ở phase 1
        
    Returns:
        List các video dict theo format template
    """
    if not video_ids:
        return []

    remaining_pct = 100 - progress_phase1_pct
    total_videos = len(video_ids)

    def detail_progress(fetched, total):
        if progress_callback:
            pct = progress_phase1_pct + int(fetched / total * remaining_pct)
            progress_callback(pct, 100, f"Đang lấy chi tiết video: {fetched}/{total}...")

    if progress_callback:
        progress_callback(progress_phase1_pct, 100,
                          f"Đang lấy chi tiết {total_videos} video...")

    details = get_video_details(api_key, video_ids, detail_progress)

    result = []
    for vid in video_ids:
        detail = details.get(vid)
        if not detail:
            continue

        result.append({
            "title": detail["title"],
            "view_count": detail["view_count"],
            "published_at": _format_date(detail["published_at"]),
            "duration": detail["duration"],
            "video_link": f"https://www.youtube.com/watch?v={vid}"
        })

    return result


def get_all_videos(api_key, channel_id, progress_callback=None):
    """
    Lấy tất cả video mới nhất từ channel (tối đa 1000).
    
    Sử dụng Uploads playlist → playlistItems API (đáng tin cậy, ít quota).
    
    Args:
        api_key: YouTube API key
        channel_id: Channel ID
        progress_callback: Hàm callback(current, total, status_text)
        
    Returns:
        List các video dict theo format template
    """
    max_videos = 1000

    # Lấy uploads playlist ID
    if progress_callback:
        progress_callback(0, 100, "Đang lấy thông tin channel...")

    channel_info = get_channel_info(api_key, channel_id)
    uploads_id = channel_info["uploads_playlist_id"]

    # Phase 1 (0-50%): Lấy danh sách video IDs từ uploads playlist
    video_ids = _fetch_video_ids_from_playlist(
        api_key, uploads_id, max_videos,
        progress_callback=lambda cur, total, msg: (
            progress_callback(int(cur / total * 50), 100, msg) if progress_callback else None
        )
    )

    # Phase 2 (50-100%): Lấy chi tiết video
    return _build_video_list(api_key, video_ids, progress_callback, progress_phase1_pct=50)


def get_latest_100(api_key, channel_id, progress_callback=None):
    """
    Lấy 100 video mới nhất từ channel.
    
    playlistItems trả về theo thứ tự mới nhất → chỉ cần lấy 100 đầu tiên.
    
    Args:
        api_key: YouTube API key
        channel_id: Channel ID
        progress_callback: Hàm callback(current, total, status_text)
        
    Returns:
        List các video dict theo format template
    """
    if progress_callback:
        progress_callback(0, 100, "Đang lấy thông tin channel...")

    channel_info = get_channel_info(api_key, channel_id)
    uploads_id = channel_info["uploads_playlist_id"]

    # Phase 1 (0-40%): Lấy 100 video IDs mới nhất
    video_ids = _fetch_video_ids_from_playlist(
        api_key, uploads_id, 100,
        progress_callback=lambda cur, total, msg: (
            progress_callback(int(cur / total * 40), 100, msg) if progress_callback else None
        )
    )

    # Phase 2 (40-100%): Lấy chi tiết
    return _build_video_list(api_key, video_ids, progress_callback, progress_phase1_pct=40)


def get_top_100_views(api_key, channel_id, progress_callback=None):
    """
    Lấy 100 video có lượt view cao nhất từ channel.
    
    Chiến lược: Lấy TẤT CẢ video (max 1000) từ uploads playlist,
    lấy chi tiết (view count), sort giảm dần, trả về top 100.
    
    Args:
        api_key: YouTube API key
        channel_id: Channel ID
        progress_callback: Hàm callback(current, total, status_text)
        
    Returns:
        List các video dict theo format template, sorted by view_count desc
    """
    max_videos = 1000

    if progress_callback:
        progress_callback(0, 100, "Đang lấy thông tin channel...")

    channel_info = get_channel_info(api_key, channel_id)
    uploads_id = channel_info["uploads_playlist_id"]

    # Phase 1 (0-40%): Lấy tất cả video IDs (max 1000) để tìm top views
    video_ids = _fetch_video_ids_from_playlist(
        api_key, uploads_id, max_videos,
        progress_callback=lambda cur, total, msg: (
            progress_callback(int(cur / total * 40), 100, msg) if progress_callback else None
        )
    )

    # Phase 2 (40-95%): Lấy chi tiết tất cả video
    all_videos = _build_video_list(api_key, video_ids, progress_callback, progress_phase1_pct=40)

    # Phase 3: Sort theo view_count giảm dần → lấy top 100
    if progress_callback:
        progress_callback(95, 100, "Đang sắp xếp theo lượt xem...")

    all_videos.sort(key=lambda v: int(v.get("view_count", "0")), reverse=True)

    if progress_callback:
        progress_callback(100, 100, "Hoàn tất!")

    return all_videos[:100]
