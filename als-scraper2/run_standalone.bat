@echo off
REM Run Standalone Scraper (Command Line Only)

echo ==================================
echo AlsTapingTools.com Scraper
echo Standalone Command Line Version
echo ==================================
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

REM Run scraper
echo.
echo Starting scraper...
echo ==================================
python als_scraper.py

echo.
echo Scraping complete! Check the following files:
echo   - alstapingtools_products.csv
echo   - alstapingtools_products.json
echo   - product_images\
echo   - scrape_report.txt
echo.
pause
