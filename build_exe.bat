@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PerfectWorldRoulette roulette.py
echo EXE готов в dist\PerfectWorldRoulette.exe
pause
