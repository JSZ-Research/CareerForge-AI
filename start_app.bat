@echo off
echo Starting CareerForge AI...

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

REM Run App
call venv\Scripts\activate.bat
streamlit run app.py
pause
