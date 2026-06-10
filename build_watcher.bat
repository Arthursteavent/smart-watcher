@echo off
echo Building Watcher UI...

cd /d "%~dp0"

pyinstaller --noconfirm --windowed --name "Watcher" --add-data "web;web" --add-data "keywords.json;." watcher_ui.py

echo Build complete.
pause
