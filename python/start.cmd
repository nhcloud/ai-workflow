@echo off
REM Workflow Lab - Launch Python Workflow Project

echo ============================================================
echo              Workflow Lab (Python) - Starting
echo ============================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create virtual environment if it doesn't exist
if not exist "%SCRIPT_DIR%.venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Running Workflow Lab...
python program.py
