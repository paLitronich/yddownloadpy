import tkinter as tk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
import threading
import os
import platform
import subprocess

CONFIG_FILE = "config.cfg"

# --- Функції для роботи з config ---
def get_output_dir():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                folder = f.read().strip()
                if folder and os.path.isdir(folder):
                    return folder
        except:
            pass
    return os.getcwd()

def save_output_dir(path):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(path)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зберегти шлях: {e}")

# --- Завантаження ---
def download_video():
    url = entry_url.get().strip()
    if not url:
        messagebox.showerror("Помилка", "Введіть посилання на YouTube!")
        return

    output_dir = entry_path.get().strip()
    if not output_dir:
        output_dir = get_output_dir()
    else:
        save_output_dir(output_dir)

    tasks = []

    # --- ВІДЕО ---
    if var_video.get():
        v_format = "bestvideo[height<=" + video_quality.get() + "]+bestaudio/best"
        v_opts = {
            "format": v_format,
            "merge_output_format": video_format.get(),
            "outtmpl": os.path.join(output_dir, "%(title).200B.%(ext)s"),
        }
        tasks.append(("Відео", v_opts))

    # --- АУДІО ---
    if var_audio.get():
        a_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(title).200B_audio.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format.get(),
                "preferredquality": audio_quality.get(),
            }],
        }
        tasks.append(("Аудіо", a_opts))

    if not tasks:
        messagebox.showerror("Помилка", "Оберіть хоча б відео або аудіо для завантаження!")
        return

    def run_download():
        try:
            for label, opts in tasks:
                with YoutubeDL(opts) as ydl:
                    ydl.download([url])
            messagebox.showinfo("Готово", "Завантаження завершене ✅")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    threading.Thread(target=run_download, daemon=True).start()

# --- Вибір/відкриття папки ---
def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)
        save_output_dir(folder)

def open_folder():
    folder = get_output_dir()
    if os.path.isdir(folder):
        try:
            os.startfile(folder)  # Windows
        except AttributeError:
            if platform.system() == "Darwin":  # macOS
                subprocess.call(["open", folder])
            else:  # Linux
                subprocess.call(["xdg-open", folder])

# --- GUI ---
root = tk.Tk()
root.title("YouTube Downloader (Video + Audio)")
root.geometry("550x450")
root.resizable(False, False)

# URL
tk.Label(root, text="Посилання на YouTube:").pack(anchor="w", padx=10, pady=5)
entry_url = tk.Entry(root, width=70)
entry_url.pack(padx=10)

# Папка для збереження
tk.Label(root, text="Папка для збереження:").pack(anchor="w", padx=10, pady=5)
frame_path = tk.Frame(root)
frame_path.pack(padx=10, fill="x")

entry_path = tk.Entry(frame_path, width=50)
entry_path.insert(0, get_output_dir())
entry_path.pack(side="left", fill="x", expand=True)

btn_browse = tk.Button(frame_path, text="Обрати", command=choose_folder)
btn_browse.pack(side="left", padx=5)

btn_open = tk.Button(frame_path, text="Відкрити", command=open_folder)
btn_open.pack(side="left", padx=5)

# --- Відео ---
frame_video = tk.LabelFrame(root, text="Налаштування Відео", padx=10, pady=5)
frame_video.pack(fill="x", padx=10, pady=10)

var_video = tk.BooleanVar(value=True)
tk.Checkbutton(frame_video, text="Завантажити відео", variable=var_video).grid(row=0, column=0, sticky="w")

tk.Label(frame_video, text="Формат:").grid(row=1, column=0, sticky="w")
video_format = tk.StringVar(value="mp4")
tk.OptionMenu(frame_video, video_format, "mp4", "mkv", "webm").grid(row=1, column=1, sticky="w")

tk.Label(frame_video, text="Макс. якість (висота):").grid(row=2, column=0, sticky="w")
video_quality = tk.StringVar(value="1080")
tk.OptionMenu(frame_video, video_quality, "144", "240", "360", "480", "720", "1080", "1440", "2160").grid(row=2, column=1, sticky="w")

# --- Аудіо ---
frame_audio = tk.LabelFrame(root, text="Налаштування Аудіо", padx=10, pady=5)
frame_audio.pack(fill="x", padx=10, pady=10)

var_audio = tk.BooleanVar(value=True)
tk.Checkbutton(frame_audio, text="Завантажити аудіо", variable=var_audio).grid(row=0, column=0, sticky="w")

tk.Label(frame_audio, text="Формат:").grid(row=1, column=0, sticky="w")
audio_format = tk.StringVar(value="mp3")
tk.OptionMenu(frame_audio, audio_format, "mp3", "m4a", "flac", "wav").grid(row=1, column=1, sticky="w")

tk.Label(frame_audio, text="Якість (kbps):").grid(row=2, column=0, sticky="w")
audio_quality = tk.StringVar(value="192")
tk.OptionMenu(frame_audio, audio_quality, "64", "128", "192", "256", "320").grid(row=2, column=1, sticky="w")

# --- Кнопка завантаження ---
btn_download = tk.Button(root, text="⬇️ Завантажити", command=download_video,
                         bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
btn_download.pack(pady=15)

root.mainloop()
