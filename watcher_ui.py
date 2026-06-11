import eel
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from watcher import start_watcher
import pystray
from PIL import Image, ImageDraw
import socket

lock_socket = None

def listen_for_show_ui():
    global lock_socket
    while True:
        try:
            data, addr = lock_socket.recvfrom(1024)
            if data == b"SHOW_UI":
                eel.show('index.html')
        except:
            break

def enforce_single_instance():
    global lock_socket
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        lock_socket.bind(('127.0.0.1', 47289))
        threading.Thread(target=listen_for_show_ui, daemon=True).start()
    except socket.error:
        # Jika instance lain sudah jalan, kirim pesan untuk memunculkan UI
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"SHOW_UI", ('127.0.0.1', 47289))
        sock.close()
        sys.exit(0)

def create_image():
    width = 64
    height = 64
    color1 = "#1e293b"
    color2 = "#3b82f6"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

# Hide root Tkinter window
root = tk.Tk()
root.withdraw()
root.update_idletasks()
try:
    _x = (root.winfo_screenwidth() // 2) - 200
    _y = (root.winfo_screenheight() // 2) - 150
    root.geometry(f"+{_x}+{_y}")
except:
    pass
root.attributes('-topmost', True)

observer = None
icon_instance = None
watch_folder = os.path.expanduser("~/Downloads")
target_folder = os.path.expanduser("~/Documents/TargetFolder")
config_file = Path(os.path.expanduser("~")) / ".smart_watcher_config.txt"

def load_config():
    global watch_folder, target_folder
    if not config_file.exists():
        with open(config_file, 'w') as f:
            import platform
            if platform.system() == "Windows":
                f.write(f"{os.path.expanduser('~')}\\Downloads\n{os.path.expanduser('~')}\\Documents\\TargetFolder")
            else:
                f.write(f"{os.path.expanduser('~')}/Downloads\n{os.path.expanduser('~')}/Documents/TargetFolder")
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                watch_folder = lines[0]
                target_folder = lines[1]
    else:
        save_config()

def save_config():
    with open(config_file, 'w') as f:
        f.write(f"{watch_folder}\n{target_folder}")

@eel.expose
def get_config():
    load_config()
    return {"watch": watch_folder, "target": target_folder, "is_running": observer is not None}

@eel.expose
def select_target_folder():
    global target_folder
    import platform
    if platform.system() == "Darwin":
        import subprocess
        script = 'set frontApp to (path to frontmost application as text)\n' \
                 'tell application frontApp\n' \
                 'activate\n' \
                 'set theFolder to choose folder with prompt "Select Destination Folder"\n' \
                 'return POSIX path of theFolder\n' \
                 'end tell'
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                folder = result.stdout.strip()
                if folder:
                    target_folder = folder
                    save_config()
                    return target_folder
        except:
            pass
        return None
    else:
        folder = filedialog.askdirectory(parent=root, title="Select Destination Folder")
        if folder:
            target_folder = folder
            save_config()
            return target_folder
        return None

@eel.expose
def is_watcher_running():
    global observer
    return observer is not None

@eel.expose
def toggle_watcher():
    global observer, icon_instance
    if observer:
        observer.stop()
        observer.join()
        observer = None
        return False
    else:
        load_config()
        
        def notify_user(msg, title):
            if icon_instance:
                try:
                    icon_instance.notify(msg, title)
                except:
                    pass
                    
        observer = start_watcher(watch_folder, target_folder, notify_user)
        return True

@eel.expose
def exit_app():
    global observer
    if observer:
        observer.stop()
        observer.join()
    os._exit(0)

def quit_app(icon, item):
    global observer
    if observer:
        observer.stop()
        observer.join()
    icon.stop()
    os._exit(0)

def show_window(icon, item):
    eel.show('index.html')

def setup_tray():
    global icon_instance
    icon_instance = pystray.Icon("WatcherUI")
    icon_instance.menu = pystray.Menu(
        pystray.MenuItem("Show UI", show_window),
        pystray.MenuItem("Exit", quit_app)
    )
    icon_instance.icon = create_image()
    icon_instance.title = "Smart Watcher"
    icon_instance.run()

if __name__ == "__main__":
    enforce_single_instance()
    load_config()
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        eel.init(os.path.join(base_dir, 'web'))
    else:
        eel.init('web')
    
    import platform
    if platform.system() == "Darwin":
        # MacOS: Hindari pystray karena memicu crash pada Main Thread + Eel Gevent.
        # Biarkan Eel berjalan di main thread (blocking), dan aplikasi akan otomatis berhenti saat UI ditutup.
        try:
            w, h = 600, 480
            x = (root.winfo_screenwidth() // 2) - (w // 2)
            y = (root.winfo_screenheight() // 2) - (h // 2)
            eel.start('index.html', size=(w, h), position=(x, y))
        except:
            eel.start('index.html', size=(600, 480))
    else:
        # Windows: Gunakan pystray di background thread, dan Eel secara non-blocking
        threading.Thread(target=setup_tray, daemon=True).start()
        
        def handle_close(route, websockets):
            pass 
            
        eel.start('index.html', size=(600, 500), port=0, disable_cache=True, block=False, close_callback=handle_close)
        while True:
            eel.sleep(1)
