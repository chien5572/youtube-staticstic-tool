"""
main.py — Giao diện chính của ứng dụng YouTube Statistic Tool.

Sử dụng Tkinter + ttk với giao diện tiếng Việt, light mode.
Chạy API calls trên background thread để GUI vẫn responsive.
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from youtube_api import (
    validate_api_key,
    extract_channel_id,
    get_channel_info,
    get_all_videos,
    get_latest_100,
    get_top_100_views,
    YouTubeAPIError,
    QuotaExceededError,
    InvalidAPIKeyError,
    ChannelNotFoundError,
)
from file_handler import (
    generate_file_pair,
    save_json,
    convert_json_to_csv,
    build_output_data,
)

# ─── Constants ────────────────────────────────────────────────────────────────

APP_TITLE = "📊 YouTube Statistic Tool"
APP_WIDTH = 580
APP_HEIGHT = 620
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# ─── Color Palette (Light Mode) ──────────────────────────────────────────────

COLORS = {
    "bg": "#F5F7FA",
    "card_bg": "#FFFFFF",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_active": "#1E40AF",
    "text": "#1E293B",
    "text_secondary": "#64748B",
    "border": "#E2E8F0",
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E1",
    "success": "#059669",
    "error": "#DC2626",
    "warning": "#D97706",
    "progress_bg": "#E2E8F0",
    "progress_fill": "#2563EB",
    "accent": "#7C3AED",
}

# ─── Config Management ───────────────────────────────────────────────────────


def load_config():
    """Đọc config từ file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def save_config(config):
    """Lưu config ra file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except IOError:
        pass


# ─── Main Application ────────────────────────────────────────────────────────


class YouTubeStatisticApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (APP_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (APP_HEIGHT // 2)
        self.root.geometry(f"+{x}+{y}")

        # Variables
        self.api_key_var = tk.StringVar()
        self.channel_url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="all")
        self.show_key_var = tk.BooleanVar(value=False)
        self.is_running = False

        # Load saved config
        config = load_config()
        if config.get("api_key"):
            self.api_key_var.set(config["api_key"])
        if config.get("output_dir"):
            self.output_dir_var.set(config["output_dir"])

        # Setup styles
        self._setup_styles()

        # Build UI
        self._build_ui()

    def _setup_styles(self):
        """Cấu hình ttk styles cho giao diện."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Frame styles
        self.style.configure("Card.TFrame", background=COLORS["card_bg"])
        self.style.configure("App.TFrame", background=COLORS["bg"])

        # Label styles
        self.style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 18, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Field.TLabel",
            background=COLORS["card_bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "Status.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Success.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["success"],
            font=("Segoe UI", 9, "bold"),
        )

        # Button styles
        self.style.configure(
            "Primary.TButton",
            background=COLORS["primary"],
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 10),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", COLORS["primary_active"]), ("disabled", "#94A3B8")],
            foreground=[("disabled", "#E2E8F0")],
        )

        self.style.configure(
            "Browse.TButton",
            background=COLORS["border"],
            foreground=COLORS["text"],
            font=("Segoe UI", 9),
            padding=(8, 4),
        )

        self.style.configure(
            "Toggle.TButton",
            background=COLORS["border"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 8),
            padding=(6, 4),
        )

        # Radiobutton styles
        self.style.configure(
            "Mode.TRadiobutton",
            background=COLORS["card_bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10),
        )

        # Progressbar styles
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS["progress_bg"],
            background=COLORS["progress_fill"],
            thickness=8,
        )

    def _build_ui(self):
        """Xây dựng giao diện chính."""
        main_frame = ttk.Frame(self.root, style="App.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # ── Title ─────────────────────────────────────
        title_label = ttk.Label(main_frame, text="📊 YouTube Statistic Tool", style="Title.TLabel")
        title_label.pack(anchor="center", pady=(0, 2))

        subtitle_label = ttk.Label(
            main_frame,
            text="Lấy dữ liệu thống kê video từ kênh YouTube",
            style="Subtitle.TLabel",
        )
        subtitle_label.pack(anchor="center", pady=(0, 15))

        # ── Card Container ────────────────────────────
        card = ttk.Frame(main_frame, style="Card.TFrame")
        card.pack(fill="x", pady=(0, 12))

        # Thêm padding bên trong card
        card_inner = ttk.Frame(card, style="Card.TFrame")
        card_inner.pack(fill="x", padx=20, pady=15)

        # ── API Key ───────────────────────────────────
        ttk.Label(card_inner, text="🔑  YouTube API Key", style="Field.TLabel").pack(anchor="w")

        key_frame = ttk.Frame(card_inner, style="Card.TFrame")
        key_frame.pack(fill="x", pady=(4, 12))

        self.api_key_entry = ttk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            show="•",
            font=("Segoe UI", 10),
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True, ipady=4)

        self.toggle_key_btn = ttk.Button(
            key_frame,
            text="👁 Hiện",
            style="Toggle.TButton",
            command=self._toggle_api_key,
            width=8,
        )
        self.toggle_key_btn.pack(side="right", padx=(8, 0))

        # ── Channel URL ──────────────────────────────
        ttk.Label(card_inner, text="🔗  Link Channel YouTube", style="Field.TLabel").pack(anchor="w")

        self.channel_entry = ttk.Entry(
            card_inner,
            textvariable=self.channel_url_var,
            font=("Segoe UI", 10),
        )
        self.channel_entry.pack(fill="x", pady=(4, 12), ipady=4)

        # ── Output Directory ─────────────────────────
        ttk.Label(card_inner, text="📁  Thư mục lưu file", style="Field.TLabel").pack(anchor="w")

        dir_frame = ttk.Frame(card_inner, style="Card.TFrame")
        dir_frame.pack(fill="x", pady=(4, 12))

        self.output_entry = ttk.Entry(
            dir_frame,
            textvariable=self.output_dir_var,
            font=("Segoe UI", 10),
        )
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=4)

        browse_btn = ttk.Button(
            dir_frame,
            text="Chọn...",
            style="Browse.TButton",
            command=self._browse_directory,
            width=8,
        )
        browse_btn.pack(side="right", padx=(8, 0))

        # ── Mode Selection ───────────────────────────
        ttk.Label(card_inner, text="⚙️  Chức năng", style="Field.TLabel").pack(anchor="w", pady=(0, 4))

        modes_frame = ttk.Frame(card_inner, style="Card.TFrame")
        modes_frame.pack(fill="x", pady=(0, 5))

        modes = [
            ("all", "📋  Tất cả video mới nhất (tối đa 1000)"),
            ("100new", "🆕  100 video mới nhất"),
            ("100views", "🔥  100 video nhiều lượt xem nhất"),
        ]

        for value, text in modes:
            rb = ttk.Radiobutton(
                modes_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                style="Mode.TRadiobutton",
            )
            rb.pack(anchor="w", pady=2)

        # ── Start Button ─────────────────────────────
        self.start_btn = ttk.Button(
            main_frame,
            text="▶  BẮT ĐẦU LẤY DỮ LIỆU",
            style="Primary.TButton",
            command=self._start_fetching,
        )
        self.start_btn.pack(fill="x", pady=(0, 12), ipady=2)

        # ── Progress Section ─────────────────────────
        progress_frame = ttk.Frame(main_frame, style="App.TFrame")
        progress_frame.pack(fill="x", pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100,
        )
        self.progress_bar.pack(fill="x", pady=(0, 6))

        self.status_label = ttk.Label(
            progress_frame,
            text="Sẵn sàng",
            style="Status.TLabel",
        )
        self.status_label.pack(anchor="w")

    def _toggle_api_key(self):
        """Toggle hiển thị/ẩn API key."""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="•")
            self.toggle_key_btn.configure(text="👁 Hiện")
            self.show_key_var.set(False)
        else:
            self.api_key_entry.configure(show="")
            self.toggle_key_btn.configure(text="🔒 Ẩn")
            self.show_key_var.set(True)

    def _browse_directory(self):
        """Mở dialog chọn thư mục output."""
        initial_dir = self.output_dir_var.get() or os.path.expanduser("~")
        directory = filedialog.askdirectory(
            title="Chọn thư mục lưu file output",
            initialdir=initial_dir,
        )
        if directory:
            self.output_dir_var.set(directory)

    def _validate_inputs(self):
        """Kiểm tra các input trước khi bắt đầu."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập YouTube API Key.")
            self.api_key_entry.focus()
            return False

        channel_url = self.channel_url_var.get().strip()
        if not channel_url:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập link channel YouTube.")
            self.channel_entry.focus()
            return False

        if "youtube.com" not in channel_url and "youtu.be" not in channel_url:
            messagebox.showwarning(
                "Link không hợp lệ",
                "Vui lòng nhập đúng link channel YouTube.\n"
                "Ví dụ: https://www.youtube.com/@TenKenh",
            )
            self.channel_entry.focus()
            return False

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn thư mục lưu file output.")
            return False

        if not os.path.isdir(output_dir):
            messagebox.showwarning(
                "Thư mục không tồn tại",
                f"Thư mục không tồn tại:\n{output_dir}\n\nVui lòng chọn thư mục khác.",
            )
            return False

        return True

    def _update_progress(self, value, maximum, status_text):
        """Cập nhật progress bar và status label từ main thread."""
        self.progress_bar["value"] = value
        self.progress_bar["maximum"] = maximum
        self.status_label.configure(text=status_text, style="Status.TLabel")

    def _start_fetching(self):
        """Bắt đầu lấy dữ liệu (chạy trên background thread)."""
        if self.is_running:
            return

        if not self._validate_inputs():
            return

        # Save config
        config = load_config()
        config["api_key"] = self.api_key_var.get().strip()
        config["output_dir"] = self.output_dir_var.get().strip()
        save_config(config)

        # Disable UI
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.progress_bar["value"] = 0

        # Start background thread
        thread = threading.Thread(target=self._fetch_worker, daemon=True)
        thread.start()

    def _fetch_worker(self):
        """Worker thread để lấy dữ liệu từ YouTube API."""
        try:
            api_key = self.api_key_var.get().strip()
            channel_url = self.channel_url_var.get().strip()
            output_dir = self.output_dir_var.get().strip()
            mode = self.mode_var.get()

            # Step 1: Validate API key
            self.root.after(0, self._update_progress, 0, 100, "Đang kiểm tra API key...")
            validate_api_key(api_key)

            # Step 2: Extract channel ID
            self.root.after(0, self._update_progress, 5, 100, "Đang tìm channel...")
            channel_id = extract_channel_id(channel_url, api_key)

            # Step 3: Get channel info (bao gồm uploads_playlist_id)
            self.root.after(0, self._update_progress, 10, 100, "Đang lấy thông tin channel...")
            channel_info = get_channel_info(api_key, channel_id)
            channel_name = channel_info["channel_name"]
            uploads_playlist_id = channel_info["uploads_playlist_id"]

            self.root.after(
                0, self._update_progress, 15, 100,
                f"Đã tìm thấy kênh: {channel_name} — Bắt đầu lấy video..."
            )

            # Step 4: Fetch videos based on mode
            def progress_callback(current, total, status):
                # Scale progress: 15-90%
                scaled = 15 + int(current / total * 75) if total > 0 else 15
                self.root.after(0, self._update_progress, scaled, 100, status)

            if mode == "all":
                videos = get_all_videos(api_key, channel_id, progress_callback)
            elif mode == "100new":
                videos = get_latest_100(api_key, channel_id, progress_callback)
            elif mode == "100views":
                videos = get_top_100_views(api_key, channel_id, progress_callback)
            else:
                videos = []

            # Step 5: Save files
            self.root.after(0, self._update_progress, 92, 100, "Đang lưu file JSON...")

            # Loại bỏ uploads_playlist_id khỏi output data
            output_channel_info = {
                "channel_name": channel_info["channel_name"],
                "channel_link": channel_info["channel_link"],
                "subcriber": channel_info["subcriber"],
                "video_num": channel_info["video_num"],
            }
            output_data = build_output_data(output_channel_info, videos)
            json_path, csv_path = generate_file_pair(channel_name, mode, output_dir)

            save_json(output_data, json_path)

            self.root.after(0, self._update_progress, 96, 100, "Đang chuyển đổi sang CSV...")
            convert_json_to_csv(json_path, csv_path)

            # Done!
            self.root.after(0, self._update_progress, 100, 100, "✅ Hoàn tất!")
            self.root.after(0, self._on_success, json_path, csv_path, len(videos))

        except (YouTubeAPIError, QuotaExceededError, InvalidAPIKeyError, ChannelNotFoundError) as e:
            self.root.after(0, self._on_error, str(e))
        except Exception as e:
            self.root.after(0, self._on_error, f"Lỗi không xác định: {str(e)}")
        finally:
            self.root.after(0, self._on_finish)

    def _on_success(self, json_path, csv_path, video_count):
        """Hiển thị thông báo thành công."""
        json_name = os.path.basename(json_path)
        csv_name = os.path.basename(csv_path)
        output_dir = os.path.dirname(json_path)

        messagebox.showinfo(
            "✅ Hoàn tất!",
            f"Đã lấy thành công {video_count} video!\n\n"
            f"📄 File JSON: {json_name}\n"
            f"📊 File CSV: {csv_name}\n"
            f"📁 Thư mục: {output_dir}",
        )

    def _on_error(self, error_message):
        """Hiển thị thông báo lỗi."""
        self.status_label.configure(text="❌ Có lỗi xảy ra", style="Status.TLabel")
        messagebox.showerror("❌ Lỗi", error_message)

    def _on_finish(self):
        """Reset UI sau khi hoàn tất (thành công hoặc lỗi)."""
        self.is_running = False
        self.start_btn.configure(state="normal")


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main():
    root = tk.Tk()

    # Set app icon (optional, skip if not available)
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass

    app = YouTubeStatisticApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
