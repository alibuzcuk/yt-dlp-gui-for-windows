import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
import sys
import time
import json
import re
from datetime import datetime, timedelta

# Translation Dictionary
translations = {
    'en': {
        'title': "YouTube Video Downloader",
        'link_label': "YouTube Link:",
        'folder_button': "Select Folder",
        'path_label_default': "No folder selected yet",
        'download_button': "Download Video",
        'message_downloading': "Video is downloading, please wait...",
        'message_success_title': "Success",
        'message_success_body': "Video downloaded successfully!",
        'error_title': "Error",
        'error_no_link': "Please enter a YouTube link.",
        'error_no_folder': "Please select download folder.",
        'error_download': "An error occurred during download: ",
        'theme_menu': "Theme",
        'light_theme': "Light Theme",
        'dark_theme': "Dark Theme",
        'checking_updates': "Checking for yt-dlp updates...",
        'updating_ytdlp': "Updating yt-dlp, please wait...",
        'update_success': "yt-dlp updated successfully!",
        'update_failed': "Failed to update yt-dlp",
        'ytdlp_uptodate': "yt-dlp is up to date",
        'download_progress': "Downloading:",
        'download_speed': "Speed:",
        'download_eta': "ETA:",
        'download_size': "Size:"
    },
    'tr': {
        'title': "YouTube Video İndirici",
        'link_label': "YouTube Linki:",
        'folder_button': "Klasör Seç",
        'path_label_default': "Henüz klasör seçilmedi",
        'download_button': "Videoyu İndir",
        'message_downloading': "Video indiriliyor, lütfen bekleyin...",
        'message_success_title': "Başarılı",
        'message_success_body': "Video başarıyla indirildi!",
        'error_title': "Hata",
        'error_no_link': "Lütfen bir YouTube linki girin.",
        'error_no_folder': "Lütfen indirme klasörünü seçin.",
        'error_download': "İndirme sırasında bir sorun oluştu: ",
        'theme_menu': "Tema",
        'light_theme': "Açık Tema",
        'dark_theme': "Karanlık Tema",
        'checking_updates': "yt-dlp güncellemeleri kontrol ediliyor...",
        'updating_ytdlp': "yt-dlp güncelleniyor, lütfen bekleyin...",
        'update_success': "yt-dlp başarıyla güncellendi!",
        'update_failed': "yt-dlp güncellemesi başarısız",
        'ytdlp_uptodate': "yt-dlp güncel",
        'download_progress': "İndiriliyor:",
        'download_speed': "Hız:",
        'download_eta': "Kalan:",
        'download_size': "Boyut:"
    },
    'ar': {
        'title': "مُنزِّل فيديوهات يوتيوب",
        'link_label': "رابط يوتيوب:",
        'folder_button': "اختيار مجلّد",
        'path_label_default': "لم يتم اختيار مجلد بعد",
        'download_button': "تحميل الفيديو",
        'message_downloading': "يتم تحميل الفيديو، يرجى الانتظار...",
        'message_success_title': "نجاح",
        'message_success_body': "تم تحميل الفيديو بنجاح!",
        'error_title': "خطأ",
        'error_no_link': "الرجاء إدخال رابط يوتيوب.",
        'error_no_folder': "الرجاء اختيار مجلد التحميل.",
        'error_download': "حدثت مشكلة أثناء التحميل: ",
        'theme_menu': "السمة",
        'light_theme': "السمة الفاتحة",
        'dark_theme': "السمة الداكنة",
        'checking_updates': "يتم التحقق من تحديثات yt-dlp...",
        'updating_ytdlp': "يتم تحديث yt-dlp، يرجى الانتظار...",
        'update_success': "تم تحديث yt-dlp بنجاح!",
        'update_failed': "فشل تحديث yt-dlp",
        'ytdlp_uptodate': "yt-dlp محدث",
        'download_progress': "التحميل:",
        'download_speed': "السرعة:",
        'download_eta': "الوقت المتبقي:",
        'download_size': "الحجم:"
    }
}

# Default language and theme - will be loaded from config later
current_lang = 'en'
current_theme = 'dark'

# Theme colors
themes = {
    'light': {
        'bg': '#ffffff',
        'fg': '#000000',
        'entry_bg': '#ffffff',
        'entry_fg': '#000000',
        'button_bg': '#f0f0f0',
        'button_fg': '#000000',
        'button_active_bg': '#e0e0e0',
        'frame_bg': '#ffffff',
        'message_fg': '#0066cc'
    },
    'dark': {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'entry_bg': '#404040',
        'entry_fg': '#ffffff',
        'button_bg': '#404040',
        'button_fg': '#ffffff',
        'button_active_bg': '#505050',
        'frame_bg': '#2b2b2b',
        'message_fg': '#4da6ff'
    }
}

def get_config_path():
    """Get the configuration file path in Documents/yt-dlp-gui folder."""
    import os
    documents_path = os.path.expanduser("~/Documents")
    config_dir = os.path.join(documents_path, "yt-dlp-gui")
    
    # Create directory if it doesn't exist
    try:
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    except:
        # Fallback to temp if Documents is not accessible
        import tempfile
        config_dir = tempfile.gettempdir()
    
    return os.path.join(config_dir, "config.json")

def load_config():
    """Load configuration from Documents/yt-dlp-gui folder."""
    config_file = get_config_path()
    default_config = {
        'last_update_check': '2000-01-01',
        'language': 'en',
        'theme': 'dark'
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config
    except:
        pass
    
    return default_config

def save_config(language=None, theme=None, update_check=None):
    """Save configuration to Documents/yt-dlp-gui folder."""
    config_file = get_config_path()
    
    # Load existing config
    config = load_config()
    
    # Update values if provided
    if language is not None:
        config['language'] = language
    if theme is not None:
        config['theme'] = theme
    if update_check is not None:
        config['last_update_check'] = update_check
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def get_last_update_check():
    """Get the last update check date from config file."""
    config = load_config()
    try:
        return datetime.fromisoformat(config.get('last_update_check', '2000-01-01'))
    except:
        return datetime(2000, 1, 1)

def save_last_update_check():
    """Save the current date as last update check."""
    save_config(update_check=datetime.now().isoformat())

def get_yt_dlp_path():
    """Get the correct yt-dlp path based on environment."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'yt-dlp.exe')
    else:
        return 'yt-dlp.exe'

def get_ffmpeg_path():
    """Get the correct ffmpeg path based on environment."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'ffmpeg.exe')
    else:
        return 'ffmpeg.exe'

def check_and_update_ytdlp():
    """Check for yt-dlp updates and update if necessary."""
    t = translations[current_lang]
    
    # Check if we need to update (check once per day)
    last_check = get_last_update_check()
    if datetime.now() - last_check < timedelta(days=1):
        return
    
    def update_process():
        try:
            message_label.config(text=t['checking_updates'])
            root.update()
            
            yt_dlp_path = get_yt_dlp_path()
            
            # Check current version
            try:
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    result = subprocess.run([yt_dlp_path, '--version'], 
                                          capture_output=True, text=True,
                                          startupinfo=startupinfo, 
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    result = subprocess.run([yt_dlp_path, '--version'], 
                                          capture_output=True, text=True)
                
                current_version = result.stdout.strip()
            except:
                current_version = "unknown"
            
            # Try to update
            message_label.config(text=t['updating_ytdlp'])
            root.update()
            
            update_cmd = [yt_dlp_path, '--update']
            
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                update_result = subprocess.run(update_cmd, capture_output=True, text=True,
                                             startupinfo=startupinfo, 
                                             creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                update_result = subprocess.run(update_cmd, capture_output=True, text=True)
            
            # Check if update was successful
            if update_result.returncode == 0:
                output = update_result.stdout.lower()
                if "updated" in output or "restart" in output:
                    message_label.config(text=t['update_success'])
                else:
                    message_label.config(text=t['ytdlp_uptodate'])
            else:
                message_label.config(text=t['update_failed'])
            
            save_last_update_check()
            
            # Clear message after 3 seconds
            root.after(3000, lambda: message_label.config(text=""))
            
        except Exception as e:
            message_label.config(text=f"{t['update_failed']}: {str(e)}")
            root.after(5000, lambda: message_label.config(text=""))
    
    # Run update check in background thread
    update_thread = threading.Thread(target=update_process)
    update_thread.daemon = True
    update_thread.start()

def apply_theme():
    """Applies the current theme to all widgets."""
    theme = themes[current_theme]
    
    # Root window
    root.configure(bg=theme['bg'])
    
    # Frame
    frame.configure(bg=theme['frame_bg'])
    
    # Labels
    link_label.configure(bg=theme['frame_bg'], fg=theme['fg'])
    path_label.configure(bg=theme['frame_bg'], fg=theme['fg'])
    message_label.configure(bg=theme['frame_bg'], fg=theme['message_fg'])
    progress_label.configure(bg=theme['frame_bg'], fg=theme['message_fg'])
    
    # Entry
    link_entry.configure(bg=theme['entry_bg'], fg=theme['entry_fg'], 
                        insertbackground=theme['entry_fg'])
    
    # Buttons
    folder_button.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                           activebackground=theme['button_active_bg'])
    indir_button.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                          activebackground=theme['button_active_bg'])
    
    # Progress bar style
    style = ttk.Style()
    if current_theme == 'dark':
        style.theme_use('clam')
        style.configure("TProgressbar",
                       background='#4da6ff',
                       troughcolor=theme['entry_bg'],
                       borderwidth=1,
                       lightcolor=theme['entry_bg'],
                       darkcolor=theme['entry_bg'])
    else:
        style.theme_use('default')
        style.configure("TProgressbar",
                       background='#0066cc',
                       troughcolor='#f0f0f0')

def set_theme(theme):
    """Changes the application theme."""
    global current_theme
    current_theme = theme
    save_config(theme=theme)  # Save theme preference
    apply_theme()

def set_language(lang):
    """Changes the application language and updates the interface."""
    global current_lang
    current_lang = lang
    save_config(language=lang)  # Save language preference
    update_interface()

def update_interface():
    """Updates all interface texts according to current language."""
    t = translations[current_lang]
    root.title(t['title'])
    link_label.config(text=t['link_label'])
    folder_button.config(text=t['folder_button'])
    if not download_path:
        path_label.config(text=t['path_label_default'])
    indir_button.config(text=t['download_button'])
    message_label.config(text="")
    
    # Update menu items
    menu_bar.entryconfig("Language / Dil / اللغة", label="Language / Dil / اللغة")
    theme_menu_label = t['theme_menu']
    for i in range(menu_bar.index("end")):
        try:
            if menu_bar.entrycget(i, "label") in ["Theme", "Tema", "السمة"]:
                menu_bar.entryconfig(i, label=theme_menu_label)
                break
        except:
            continue

def klasor_sec():
    """Allows user to select download folder."""
    global download_path
    download_path = filedialog.askdirectory()
    if download_path:
        path_label.config(text=f"Folder: {download_path}")
        message_label.config(text="")

def update_progress_bar(progress_text, progress_value=0):
    """Update progress bar and progress label."""
    progress_label.config(text=progress_text)
    progress_bar['value'] = progress_value
    root.update_idletasks()

def parse_progress_line(line):
    """Parse yt-dlp progress line and extract information."""
    # Look for progress percentage
    progress_match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
    if not progress_match:
        return None, None, None, None
    
    percentage = float(progress_match.group(1))
    
    # Look for speed
    speed_match = re.search(r'at\s+([\d.]+(?:KiB|MiB|GiB|B)/s)', line)
    speed = speed_match.group(1) if speed_match else "Unknown"
    
    # Look for ETA
    eta_match = re.search(r'ETA\s+([\d:]+)', line)
    eta = eta_match.group(1) if eta_match else "Unknown"
    
    # Look for file size
    size_match = re.search(r'of\s+([\d.]+(?:KiB|MiB|GiB|B))', line)
    size = size_match.group(1) if size_match else "Unknown"
    
    return percentage, speed, eta, size

def run_download(link):
    """Runs download process in a separate thread."""
    t = translations[current_lang]
    
    yt_dlp_path = get_yt_dlp_path()
    ffmpeg_path = get_ffmpeg_path()

    try:
        output_template = os.path.join(download_path, "%(title)s.%(ext)s")
        
        # İlk deneme: En iyi kalite
        komut = [
            yt_dlp_path,
            "-f", "best[height<=1080]/best",
            "--merge-output-format", "mp4",
            "--ffmpeg-location", ffmpeg_path,
            "--no-check-certificates",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--progress",  # Enable progress output
            "-o", output_template,
            link
        ]
        
        # Reset progress bar
        update_progress_bar(t['message_downloading'], 0)
        
        # Run with real-time output capture
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=True, startupinfo=startupinfo,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            process = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=True)
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                # Parse progress information
                percentage, speed, eta, size = parse_progress_line(line)
                
                if percentage is not None:
                    # Update progress bar with detailed info
                    progress_text = f"{t['download_progress']} {percentage:.1f}%"
                    if speed != "Unknown":
                        progress_text += f" | {t['download_speed']} {speed}"
                    if eta != "Unknown":
                        progress_text += f" | {t['download_eta']} {eta}"
                    
                    update_progress_bar(progress_text, percentage)
                
                # Check for completion
                if "100%" in line or "download completed" in line.lower():
                    update_progress_bar(f"{t['download_progress']} 100% - Finalizing...", 100)
        
        process.wait()
        
        # If first attempt failed, try alternative format
        if process.returncode != 0:
            update_progress_bar("Trying alternative format...", 0)
            
            komut_alt = [
                yt_dlp_path,
                "-f", "worst[height>=480]/worst",
                "--merge-output-format", "mp4",
                "--ffmpeg-location", ffmpeg_path,
                "--no-check-certificates",
                "--progress",
                "-o", output_template,
                link
            ]
            
            if sys.platform == "win32":
                process = subprocess.Popen(komut_alt, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         universal_newlines=True, startupinfo=startupinfo,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                process = subprocess.Popen(komut_alt, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         universal_newlines=True)
            
            # Read output for alternative format
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    percentage, speed, eta, size = parse_progress_line(line)
                    
                    if percentage is not None:
                        progress_text = f"{t['download_progress']} {percentage:.1f}%"
                        if speed != "Unknown":
                            progress_text += f" | {t['download_speed']} {speed}"
                        if eta != "Unknown":
                            progress_text += f" | {t['download_eta']} {eta}"
                        
                        update_progress_bar(progress_text, percentage)
                    
                    if "100%" in line or "download completed" in line.lower():
                        update_progress_bar(f"{t['download_progress']} 100% - Finalizing...", 100)
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Download failed with both formats")
        
        update_progress_bar("Download completed successfully!", 100)
        messagebox.showinfo(t['message_success_title'], t['message_success_body'])
        
    except Exception as e:
        update_progress_bar("Download failed!", 0)
        messagebox.showerror(t['error_title'], f"{t['error_download']}{e}")
        
    indir_button.config(state=tk.NORMAL)
    # Clear progress after 3 seconds
    root.after(3000, lambda: (update_progress_bar("", 0)))

def indir_video():
    """Function that starts the download process."""
    t = translations[current_lang]
    global download_path
    video_link = link_entry.get()
    
    if not video_link:
        messagebox.showerror(t['error_title'], t['error_no_link'])
        return

    if not download_path:
        messagebox.showerror(t['error_title'], t['error_no_folder'])
        return

    indir_button.config(state=tk.DISABLED)
    message_label.config(text=t['message_downloading'])
    
    download_thread = threading.Thread(target=run_download, args=(video_link,))
    download_thread.start()

# GUI Setup
root = tk.Tk()
root.title(translations[current_lang]['title'])
root.geometry("550x350")

download_path = ""

# Create main frame
frame = tk.Frame(root, padx=15, pady=15)
frame.pack(padx=15, pady=15, fill="both", expand=True)

# Create widgets
link_label = tk.Label(frame, text=translations[current_lang]['link_label'], font=("Arial", 10))
link_label.grid(row=0, column=0, pady=8, sticky="W")

link_entry = tk.Entry(frame, width=45, font=("Arial", 10))
link_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

folder_button = tk.Button(frame, text=translations[current_lang]['folder_button'], 
                         command=klasor_sec, font=("Arial", 10), relief="raised", bd=2)
folder_button.grid(row=1, column=0, pady=8, sticky="W")

path_label = tk.Label(frame, text=translations[current_lang]['path_label_default'], 
                     font=("Arial", 9))
path_label.grid(row=1, column=1, pady=8, sticky="W", padx=(10, 0))

indir_button = tk.Button(frame, text=translations[current_lang]['download_button'], 
                        command=indir_video, font=("Arial", 11, "bold"), 
                        relief="raised", bd=2, height=2)
indir_button.grid(row=2, column=0, columnspan=2, pady=15)

# Progress bar
progress_bar = ttk.Progressbar(frame, length=400, mode='determinate', maximum=100)
progress_bar.grid(row=3, column=0, columnspan=2, pady=8, sticky="ew")

# Progress label
progress_label = tk.Label(frame, text="", font=("Arial", 9))
progress_label.grid(row=4, column=0, columnspan=2, pady=5)

message_label = tk.Label(frame, text="", font=("Arial", 9))
message_label.grid(row=5, column=0, columnspan=2, pady=8)

# Create menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Language menu
lang_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Language / Dil / اللغة", menu=lang_menu)
lang_menu.add_command(label="English", command=lambda: set_language('en'))
lang_menu.add_command(label="Türkçe", command=lambda: set_language('tr'))
lang_menu.add_command(label="العربية", command=lambda: set_language('ar'))

# Theme menu
theme_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label=translations[current_lang]['theme_menu'], menu=theme_menu)
theme_menu.add_command(label=translations[current_lang]['light_theme'], 
                      command=lambda: set_theme('light'))
theme_menu.add_command(label=translations[current_lang]['dark_theme'], 
                      command=lambda: set_theme('dark'))

# Apply initial theme and language
apply_theme()
update_interface()

# Load config and apply saved settings
try:
    config = load_config()
    saved_lang = config.get('language', 'en')
    saved_theme = config.get('theme', 'dark')
    
    # Apply saved settings
    if saved_lang != current_lang:
        set_language(saved_lang)
    if saved_theme != current_theme:
        set_theme(saved_theme)
except:
    pass  # Use defaults if config loading fails

# Check for yt-dlp updates on startup
root.after(1000, check_and_update_ytdlp)

root.update()
time.sleep(0.5)

root.mainloop()
