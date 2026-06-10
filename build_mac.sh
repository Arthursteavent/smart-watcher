#!/bin/bash
echo "=========================================="
echo " Building Smart Watcher for macOS..."
echo "=========================================="

# Pastikan script dijalankan di macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: Script ini hanya bisa dijalankan di sistem operasi macOS."
    exit 1
fi

VENV_DIR="build_env_mac"

# 1. Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating Virtual Environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual Environment already exists."
fi

PYTHON_CMD="$VENV_DIR/bin/python"

# 2. Install Requirements
echo "[2/4] Installing requirements..."
"$PYTHON_CMD" -m pip install -r requirements.txt

# 3. Check & Install PyInstaller
echo "[3/4] Installing PyInstaller..."
"$PYTHON_CMD" -m pip install pyinstaller

# 4. Build the Application
echo "[4/4] Building the application executable..."
rm -rf build dist
"$PYTHON_CMD" -m PyInstaller --noconfirm --onedir --windowed --name "SmartWatcher" --add-data "web:web" --add-data "keywords.json:." watcher_ui.py

# ==============================================================
# BUG FIX MAC: Hapus Karantina & Berikan Akses Executable
# ==============================================================
echo "Memperbaiki perizinan aplikasi Mac (xattr & chmod)..."
xattr -cr "dist/SmartWatcher.app"
chmod +x "dist/SmartWatcher.app/Contents/MacOS/SmartWatcher"

# 5. Packaging into .dmg
echo "[5/5] Packaging dist/SmartWatcher.dmg..."
STAGE="$(mktemp -d)/dmg"
mkdir -p "$STAGE"
cp -R "dist/SmartWatcher.app" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "dist/SmartWatcher.dmg"
hdiutil create -volname "SmartWatcher" -srcfolder "$STAGE" -ov -format UDZO "dist/SmartWatcher.dmg" >/dev/null
rm -rf "$STAGE"

echo ""
echo "=========================================="
echo " Build Complete!"
echo "=========================================="
echo "Aplikasi Anda berada di folder 'dist'."
echo "Silakan cek file bernama:"
echo "  - dist/SmartWatcher.app (Aplikasi langsung)"
echo "  - dist/SmartWatcher.dmg (Installer)"
echo ""
echo "Anda bisa membagikan berkas 'SmartWatcher.dmg' kepada pengguna Mac lain."
