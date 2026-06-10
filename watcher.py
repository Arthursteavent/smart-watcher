import os
import time
import threading
import shutil
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from local_categorizer import categorize_file
import pystray
from PIL import Image, ImageDraw

def create_image():
    width = 64
    height = 64
    color1 = "#2c3e50"
    color2 = "#3498db"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, target_dir, notify_callback=None):
        super().__init__()
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.notify = notify_callback
        self.processing = set()
        self.lock = threading.Lock()
        
    def process_file(self, file_path):
        with self.lock:
            if file_path in self.processing:
                return
            self.processing.add(file_path)
            
        try:
            path = Path(file_path)
            
            if path.suffix.lower() in ['.crdownload', '.part', '.tmp', '.download']:
                return

            try:
                initial_size = -1
                while True:
                    if not path.exists():
                        return
                    current_size = path.stat().st_size
                    if current_size == initial_size and current_size > 0:
                        break
                    initial_size = current_size
                    time.sleep(1.0)
            except Exception as e:
                return
                
            time.sleep(0.5)
            
            # Check again if file still exists after sleep
            if not path.exists():
                return
            
            try:
                category, subcategory = categorize_file(str(path))
                if subcategory:
                    full_category = f"{category}\\{subcategory}"
                else:
                    full_category = category

                dest_folder = self.target_dir / full_category
                dest_folder.mkdir(parents=True, exist_ok=True)
                
                dest_path = dest_folder / path.name
                
                counter = 1
                while dest_path.exists():
                    dest_path = dest_folder / f"{path.stem}_{counter}{path.suffix}"
                    counter += 1
                    
                shutil.move(str(path), str(dest_path))
                print(f"Categorized and moved to: {full_category}")
                if self.notify:
                    self.notify(f"Dipindahkan ke kategori: {full_category}", f"File '{path.name}' Selesai!")
                
            except Exception as e:
                print(f"Error moving {path.name}: {e}")
        finally:
            with self.lock:
                if file_path in self.processing:
                    self.processing.remove(file_path)

    def on_created(self, event):
        if not event.is_directory:
            threading.Thread(target=self.process_file, args=(event.src_path,), daemon=True).start()

    def on_moved(self, event):
        if not event.is_directory:
            threading.Thread(target=self.process_file, args=(event.dest_path,), daemon=True).start()
            
    def on_modified(self, event):
        if not event.is_directory:
            threading.Thread(target=self.process_file, args=(event.src_path,), daemon=True).start()

def start_watcher(watch_folder, target_folder, notify_callback=None):
    watch_path = Path(watch_folder)
    watch_path.mkdir(parents=True, exist_ok=True)
    
    event_handler = DownloadHandler(target_folder, notify_callback)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()
    return observer
