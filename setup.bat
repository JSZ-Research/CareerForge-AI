@echo off
echo ===========================================
echo CareerForge AI: Windows Setup
echo ===========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM Create Virtual Environment if not exists
if not exist "venv" (
    echo Creating virtual environment (venv)...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate and Install
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo ===========================================
echo Setup Complete!
echo You can now run 'start_app.bat'
echo ===========================================
pause
