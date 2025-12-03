import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import sys
import json
import time
from datetime import datetime, timedelta
import yt_dlp

# Translation Dictionary
translations = {
    'en': {
        'title': "YouTube Downloader",
        'link_label': "YouTube Link:",
        'folder_button': "Select Folder",
        'path_label_default': "No folder selected yet",
        'download_button': "Download",
        'message_downloading': "Downloading, please wait...",
        'message_success_title': "Success",
        'message_success_body': "Download completed successfully!",
        'error_title': "Error",
        'error_no_link': "Please enter a YouTube link.",
        'error_no_folder': "Please select a download folder.",
        'download_progress': "Downloading:",
        'download_speed': "Speed:",
        'download_eta': "ETA:",
        'type_label': "Download Type:",
        'video_type': "Video",
        'audio_type': "MP3"
    },
    'tr': {
        'title': "YouTube İndirici",
        'link_label': "YouTube Linki:",
        'folder_button': "Klasör Seç",
        'path_label_default': "Henüz klasör seçilmedi",
        'download_button': "İndir",
        'message_downloading': "İndiriliyor, lütfen bekleyin...",
        'message_success_title': "Başarılı",
        'message_success_body': "İndirme tamamlandı!",
        'error_title': "Hata",
        'error_no_link': "Lütfen bir YouTube linki girin.",
        'error_no_folder': "Lütfen indirme klasörünü seçin.",
        'download_progress': "İndiriliyor:",
        'download_speed': "Hız:",
        'download_eta': "Kalan:",
        'type_label': "İndirme Türü:",
        'video_type': "Video",
        'audio_type': "MP3"
    },
    'ar': {
        'title': "مُنزِّل فيديوهات يوتيوب",
        'link_label': "رابط يوتيوب:",
        'folder_button': "اختيار مجلّد",
        'path_label_default': "لم يتم اختيار مجلد بعد",
        'download_button': "تحميل",
        'message_downloading': "يتم التحميل، يرجى الانتظار...",
        'message_success_title': "نجاح",
        'message_success_body': "تم التحميل بنجاح!",
        'error_title': "خطأ",
        'error_no_link': "يرجى إدخال رابط يوتيوب.",
        'error_no_folder': "يرجى اختيار مجلد التحميل.",
        'download_progress': "جار التحميل:",
        'download_speed': "السرعة:",
        'download_eta': "الوقت المتبقي:",
        'type_label': "نوع التحميل:",
        'video_type': "فيديو",
        'audio_type': "MP3"
    }
}

# Default language and theme
current_lang = 'en'
current_theme = 'dark'

# Theme colors
themes = {
    'light': {
        'bg': '#ffffff', 'fg': '#000000',
        'entry_bg': '#ffffff', 'entry_fg': '#000000',
        'button_bg': '#f0f0f0', 'button_fg': '#000000',
        'button_active_bg': '#e0e0e0',
        'frame_bg': '#ffffff',
        'message_fg': '#0066cc'
    },
    'dark': {
        'bg': '#2b2b2b', 'fg': '#ffffff',
        'entry_bg': '#404040', 'entry_fg': '#ffffff',
        'button_bg': '#404040', 'button_fg': '#ffffff',
        'button_active_bg': '#505050',
        'frame_bg': '#2b2b2b',
        'message_fg': '#4da6ff'
    }
}

# Config functions
def get_config_path():
    documents_path = os.path.expanduser("~/Documents")
    config_dir = os.path.join(documents_path, "yt-dlp-gui")
    try:
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    except:
        import tempfile
        config_dir = tempfile.gettempdir()
    return os.path.join(config_dir, "config.json")

def load_config():
    config_file = get_config_path()
    default_config = {'language': 'en','theme': 'dark'}
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
    except:
        pass
    return default_config

def save_config(language=None, theme=None):
    config_file = get_config_path()
    config = load_config()
    if language: config['language'] = language
    if theme: config['theme'] = theme
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

# Theme and language
def apply_theme():
    theme = themes[current_theme]
    root.configure(bg=theme['bg'])
    frame.configure(bg=theme['frame_bg'])
    link_label.configure(bg=theme['frame_bg'], fg=theme['fg'])
    path_label.configure(bg=theme['frame_bg'], fg=theme['fg'])
    message_label.configure(bg=theme['frame_bg'], fg=theme['message_fg'])
    progress_label.configure(bg=theme['frame_bg'], fg=theme['message_fg'])
    link_entry.configure(bg=theme['entry_bg'], fg=theme['entry_fg'], insertbackground=theme['entry_fg'])
    folder_button.configure(bg=theme['button_bg'], fg=theme['button_fg'], activebackground=theme['button_active_bg'])
    indir_button.configure(bg=theme['button_bg'], fg=theme['button_fg'], activebackground=theme['button_active_bg'])
    style = ttk.Style()
    if current_theme == 'dark':
        style.theme_use('clam')
        style.configure("TProgressbar", background='#4da6ff', troughcolor=theme['entry_bg'])
    else:
        style.theme_use('default')
        style.configure("TProgressbar", background='#0066cc', troughcolor='#f0f0f0')

def set_theme(theme):
    global current_theme
    current_theme = theme
    save_config(theme=theme)
    apply_theme()

def set_language(lang):
    global current_lang
    current_lang = lang
    save_config(language=lang)
    update_interface()

def update_interface():
    t = translations[current_lang]
    root.title(t['title'])
    link_label.config(text=t['link_label'])
    folder_button.config(text=t['folder_button'])
    indir_button.config(text=t['download_button'])
    type_label.config(text=t['type_label'])
    type_video.config(text=t['video_type'])
    type_audio.config(text=t['audio_type'])
    if not download_path:
        path_label.config(text=t['path_label_default'])
    message_label.config(text="")

# Folder selection
def klasor_sec():
    global download_path
    download_path = filedialog.askdirectory()
    if download_path:
        path_label.config(text=f"Folder: {download_path}")
        message_label.config(text="")

# Progress bar update
def update_progress_bar(progress_text, progress_value=0):
    progress_label.config(text=progress_text)
    progress_bar['value'] = progress_value
    root.update_idletasks()

# Download function
def run_download(link):
    t = translations[current_lang]
    try:
        ydl_opts = {}
        if download_type.get() == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'format': 'best[height<=1080]/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
            }

        update_progress_bar(t['message_downloading'], 0)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        messagebox.showinfo(t['message_success_title'], t['message_success_body'])
        update_progress_bar("Download completed!", 100)
    except Exception as e:
        messagebox.showerror(t['error_title'], f"{e}")
        update_progress_bar("Download failed!", 0)
    indir_button.config(state=tk.NORMAL)

def progress_hook(d):
    t = translations[current_lang]
    if d['status'] == 'downloading':
        percentage = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('eta', 'N/A')
        progress_text = f"{t['download_progress']} {percentage} | {t['download_speed']} {speed} | {t['download_eta']} {eta}"
        update_progress_bar(progress_text)

def indir_video():
    video_link = link_entry.get()
    t = translations[current_lang]
    if not video_link:
        messagebox.showerror(t['error_title'], t['error_no_link'])
        return
    if not download_path:
        messagebox.showerror(t['error_title'], t['error_no_folder'])
        return
    indir_button.config(state=tk.DISABLED)
    message_label.config(text=t['message_downloading'])
    threading.Thread(target=run_download, args=(video_link,)).start()

# GUI Setup
root = tk.Tk()
root.title(translations[current_lang]['title'])
root.geometry("550x400")
download_path = ""
frame = tk.Frame(root, padx=15, pady=15)
frame.pack(padx=15, pady=15, fill="both", expand=True)

link_label = tk.Label(frame, font=("Arial", 10))
link_label.grid(row=0, column=0, pady=8, sticky="W")
link_entry = tk.Entry(frame, width=45, font=("Arial", 10))
link_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

folder_button = tk.Button(frame, command=klasor_sec, font=("Arial", 10), relief="raised", bd=2)
folder_button.grid(row=1, column=0, pady=8, sticky="W")
path_label = tk.Label(frame, font=("Arial", 9))
path_label.grid(row=1, column=1, pady=8, sticky="W", padx=(10, 0))

type_label = tk.Label(frame, font=("Arial", 10))
type_label.grid(row=2, column=0, pady=8, sticky="W")
download_type = tk.StringVar(value="video")
type_video = tk.Radiobutton(frame, variable=download_type, value="video", font=("Arial", 10))
type_video.grid(row=2, column=1, sticky="W", padx=(10,0))
type_audio = tk.Radiobutton(frame, variable=download_type, value="audio", font=("Arial", 10))
type_audio.grid(row=2, column=1, sticky="W", padx=(80,0))

indir_button = tk.Button(frame, command=indir_video, font=("Arial", 11, "bold"), relief="raised", bd=2, height=2)
indir_button.grid(row=3, column=0, columnspan=2, pady=15)

progress_bar = ttk.Progressbar(frame, length=400, mode='determinate', maximum=100)
progress_bar.grid(row=4, column=0, columnspan=2, pady=8, sticky="ew")
progress_label = tk.Label(frame, font=("Arial", 9))
progress_label.grid(row=5, column=0, columnspan=2, pady=5)
message_label = tk.Label(frame, font=("Arial", 9))
message_label.grid(row=6, column=0, columnspan=2, pady=8)

# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

lang_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Language / Dil / اللغة", menu=lang_menu)
lang_menu.add_command(label="English", command=lambda: set_language('en'))
lang_menu.add_command(label="Türkçe", command=lambda: set_language('tr'))
lang_menu.add_command(label="العربية", command=lambda: set_language('ar'))

theme_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Theme / Tema", menu=theme_menu)
theme_menu.add_command(label="Light Theme", command=lambda: set_theme('light'))
theme_menu.add_command(label="Dark Theme", command=lambda: set_theme('dark'))

# Load config
try:
    config = load_config()
    set_language(config.get('language', 'en'))
    set_theme(config.get('theme', 'dark'))
except:
    pass

apply_theme()
update_interface()
root.mainloop()
