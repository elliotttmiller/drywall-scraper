#!/bin/bash
# Run Web Application Version

echo "========================================="
echo "AlsTapingTools.com Scraper"
echo "Web Application with Visual Interface"
echo "========================================="
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

# Create static directory
mkdir -p static

# Run web app
echo ""
echo "Starting web server..."
echo "========================================="
echo ""
echo "  🌐 Open your browser and go to:"
echo "  👉 http://localhost:5000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

python app.py
