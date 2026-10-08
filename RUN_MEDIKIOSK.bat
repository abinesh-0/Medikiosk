@echo off
setlocal
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo [1/2] Creating virtual environment...
  py -m venv venv
)
echo [2/2] Starting MediKiosk...
call venv\Scripts\activate.bat
python app.py
pause
