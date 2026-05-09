@echo off
cd /d %~dp0
echo Starting Task Tracker Enterprise Web Application...
echo.
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
set HOST=0.0.0.0
set PORT=5000
set SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_SECRET
python production_server.py
pause
