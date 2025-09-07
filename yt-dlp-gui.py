import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys
import time

if getattr(sys, 'frozen', False):
    yt_dlp_path = os.path.join(sys._MEIPASS, 'yt-dlp.exe')
    ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
else:
    yt_dlp_path = 'yt-dlp.exe'
    ffmpeg_path = 'ffmpeg.exe'

def klasor_sec():
    """Kullanıcının indirme klasörünü seçmesini sağlar."""
    global download_path
    download_path = filedialog.askdirectory()
    if download_path:
        path_label.config(text=f"Klasör: {download_path}")
        message_label.config(text="") 

def run_download(link):
    """İndirme işlemini ayrı bir thread'de çalıştırır."""
    try:
        output_template = os.path.join(download_path, "%(title)s.%(ext)s")
        
        komut = [
            yt_dlp_path,
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "--ffmpeg-location", ffmpeg_path,
            "-o", output_template,
            link
        ]
        
        subprocess.run(komut, check=True)
        
        messagebox.showinfo("Başarılı", "Video başarıyla indirildi!")
        
    except Exception as e:
        messagebox.showerror("Hata", f"İndirme sırasında bir sorun oluştu: {e}")
        
    indir_button.config(state=tk.NORMAL)
    message_label.config(text="")

def indir_video():
    """İndirme işlemini başlatan fonksiyon."""
    global download_path
    video_link = link_entry.get()
    
    if not video_link:
        messagebox.showerror("Hata", "Lütfen bir YouTube linki girin.")
        return

    if not download_path:
        messagebox.showerror("Hata", "Lütfen indirme klasörünü seçin.")
        return

    indir_button.config(state=tk.DISABLED)
    message_label.config(text="Video indiriliyor, lütfen bekleyin...")
    
    download_thread = threading.Thread(target=run_download, args=(video_link,))
    download_thread.start()

root = tk.Tk()
root.title("YouTube Video İndirici")
root.geometry("450x250")

download_path = ""

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

link_label = tk.Label(frame, text="YouTube Linki:")
link_label.grid(row=0, column=0, pady=5, sticky="W")

link_entry = tk.Entry(frame, width=40)
link_entry.grid(row=0, column=1, pady=5)

folder_button = tk.Button(frame, text="Klasör Seç", command=klasor_sec)
folder_button.grid(row=1, column=0, pady=5, sticky="W")

path_label = tk.Label(frame, text="Henüz klasör seçilmedi")
path_label.grid(row=1, column=1, pady=5, sticky="W")

indir_button = tk.Button(frame, text="Videoyu İndir", command=indir_video)
indir_button.grid(row=2, column=0, columnspan=2, pady=10)

message_label = tk.Label(frame, text="", fg="blue")
message_label.grid(row=3, column=0, columnspan=2, pady=5)

root.update()
time.sleep(1)

root.mainloop()