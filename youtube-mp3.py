# YouTubeの動画をMP3に変換してダウンロードするアプリ（進捗バー付き）
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from pydub import AudioSegment
import yt_dlp

# --- ffmpegパスの設定 ---
if getattr(sys, 'frozen', False):  # exe化されている場合
    ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
else:
    ffmpeg_path = "ffmpeg"  # 通常は PATH から呼ばれる

# pydub に ffmpeg の場所を教える
AudioSegment.converter = ffmpeg_path

class YouTubeMP3Downloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Downloader")
        self.root.geometry("420x250")

        # --- UIパーツ ---
        self.url_label = tk.Label(root, text="YouTube URL:")
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=55)
        self.url_entry.pack(pady=5)

        self.download_button = tk.Button(root, text="Download MP3", command=self.start_download_thread)
        self.download_button.pack(pady=10)

        self.progress_label = tk.Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
        self.progress_bar.pack(pady=5)

    # --- ダウンロードスレッド開始 ---
    def start_download_thread(self):
        thread = threading.Thread(target=self.download_mp3)
        thread.start()

    # --- ダウンロード進捗コールバック ---
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = downloaded / total * 100
                self.progress_bar['value'] = percent
                self.progress_label.config(text=f"Progress: {percent:.1f}%")
                self.root.update_idletasks()

        elif d['status'] == 'finished':
            self.progress_label.config(text="Converting to MP3...")

    # --- メイン処理 ---
    def download_mp3(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        output_path = filedialog.askdirectory(title="Select Download Folder")
        if not output_path:
            return

        self.download_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting download...")

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.progress_bar['value'] = 100
            self.progress_label.config(text="Completed!")
            messagebox.showinfo("Success", "Download and conversion completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.download_button.config(state='normal')

# --- アプリ起動 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMP3Downloader(root)
    root.mainloop()
