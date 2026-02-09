@echo off
REM Run Web Application Version

echo =========================================
echo AlsTapingTools.com Scraper
echo Web Application with Visual Interface
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Create static directory
if not exist "static" mkdir static

REM Run web app
echo.
echo Starting web server...
echo =========================================
echo.
echo   🌐 Open your browser and go to:
echo   👉 http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo.
echo =========================================
echo.

python app.py
