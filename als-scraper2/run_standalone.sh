#!/bin/bash
# Run Standalone Scraper (Command Line Only)

echo "=================================="
echo "AlsTapingTools.com Scraper"
echo "Standalone Command Line Version"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run scraper
echo ""
echo "Starting scraper..."
echo "=================================="
python als_scraper.py

echo ""
echo "Scraping complete! Check the following files:"
echo "  - alstapingtools_products.csv"
echo "  - alstapingtools_products.json"
echo "  - product_images/"
echo "  - scrape_report.txt"
echo ""
