import os
import sys
import subprocess
import platform

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.check_call(cmd, shell=True)

def main():
    print("=== Smart Watcher Installer Builder ===")
    
    base_python = sys.executable

    # 1. Create Virtual Environment
    print("\n[1/4] Creating Virtual Environment...")
    venv_dir = "build_env"
    if not os.path.exists(venv_dir):
        run_cmd(f'"{base_python}" -m venv {venv_dir}')
    
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")

    # 2. Install Requirements
    print("\n[2/4] Installing requirements...")
    run_cmd(f'"{python_cmd}" -m pip install -r requirements.txt')
    
    # 3. Check & Install PyInstaller
    print("\n[3/4] Checking & Installing PyInstaller...")
    run_cmd(f'"{python_cmd}" -m pip install pyinstaller')

    # 4. Build the Application
    print("\n[4/4] Building the application executable...")
    separator = ";" if platform.system() == "Windows" else ":"
    
    # Kami menggunakan --onedir (bukan --onefile) khusus untuk Watcher karena menggunakan UI web (Eel)
    # Jika dipaksa --onefile, UI Web seringkali gagal dimuat di komputer lain karena file HTML tidak ditemukan.
    if platform.system() == "Windows":
        cmd = f'"{python_cmd}" -m PyInstaller --noconfirm --onefile --windowed --name "SmartWatcher" --add-data "web{separator}web" --add-data "keywords.json{separator}." watcher_ui.py'
    else:
        cmd = f'"{python_cmd}" -m PyInstaller --noconfirm --onedir --windowed --name "SmartWatcher" --add-data "web{separator}web" --add-data "keywords.json{separator}." watcher_ui.py'

    run_cmd(cmd)

    if platform.system() == "Darwin":
        print("\n[5/5] Creating .dmg Installer for Mac...")
        dmg_staging = "dist/dmg_staging"
        os.makedirs(dmg_staging, exist_ok=True)
        run_cmd(f'cp -R "dist/SmartWatcher.app" "{dmg_staging}/"')
        run_cmd(f'ln -s /Applications "{dmg_staging}/Applications"')
        run_cmd(f'hdiutil create -volname "SmartWatcher" -srcfolder "{dmg_staging}" -ov -format UDZO "dist/SmartWatcher.dmg"')
        run_cmd(f'rm -rf "{dmg_staging}"')

    print("\n=== Build Complete! ===")
    if platform.system() == "Windows":
        print("Sukses! Anda bisa menemukan folder aplikasi 'SmartWatcher' di dalam folder 'dist'.")
        print("Tinggal klik kanan file SmartWatcher.exe lalu pilih 'Send to -> Desktop (create shortcut)'.")
    else:
        print("Sukses! Anda bisa menemukan installer 'SmartWatcher.dmg' di dalam folder 'dist'.")
        print("File DMG tersebut siap untuk dibagikan. User hanya perlu membukanya dan men-drag aplikasi ke folder Applications.")

if __name__ == "__main__":
    main()
