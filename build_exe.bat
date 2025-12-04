@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building Executable...
python -m PyInstaller --noconsole --onefile --name "ProcessMonitor" --clean main.py

echo Build Complete.
pause
