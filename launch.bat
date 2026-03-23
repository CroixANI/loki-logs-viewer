@echo off
title LogLens - Log Viewer
echo.
echo  =========================================
echo    LogLens - Log Viewer
echo  =========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

:: Install dependencies if needed
echo  Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo  Installing dependencies...
    pip install -r requirements.txt --quiet
)

echo  Starting LogLens...
echo  Open your browser at: http://localhost:8501
echo.
streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false
pause
