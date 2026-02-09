#!/usr/bin/env python3
"""
Flask Web Application for AlsTapingTools.com Scraper
Provides a web interface to run and monitor the scraping process
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import threading
import os
import sys
from als_scraper import AlsTapingToolsScraper
import json
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scraper instance and status
scraper = None
scraping_status = {
    'is_running': False,
    'progress': 0,
    'status_message': 'Ready',
    'products_found': 0,
    'pages_visited': 0,
    'current_url': '',
    'logs': []
}

def add_log(message, log_type='info'):
    """Add a log message to the status"""
    global scraping_status
    scraping_status['logs'].append({
        'message': message,
        'type': log_type,
        'timestamp': str(datetime.now())
    })
    logger.info(f"[{log_type}] {message}")

def run_scraper_thread(url, delay, download_images):
    """Run the scraper in a separate thread"""
    global scraper, scraping_status
    
    try:
        scraping_status['is_running'] = True
        scraping_status['progress'] = 0
        scraping_status['logs'] = []
        
        add_log('Initializing scraper...', 'info')
        scraper = AlsTapingToolsScraper(base_url=url)
        scraper.delay = delay
        
        add_log('Starting website crawl...', 'info')
        scraping_status['progress'] = 10
        scraping_status['status_message'] = 'Discovering pages...'
        
        # Discover all pages
        all_pages = scraper.discover_all_pages()
        scraping_status['pages_visited'] = len(all_pages)
        add_log(f'Found {len(all_pages)} pages', 'success')
        
        scraping_status['progress'] = 30
        scraping_status['status_message'] = 'Extracting products...'
        
        # Scrape products
        total_pages = len(all_pages)
        for idx, page_url in enumerate(all_pages):
            if page_url in scraper.visited_urls:
                continue
                
            scraper.visited_urls.add(page_url)
            scraping_status['current_url'] = page_url
            
            product_data = scraper.extract_product_data(page_url)
            
            if product_data:
                scraper.products.append(product_data)
                scraping_status['products_found'] = len(scraper.products)
                add_log(f'Product found: {product_data["product_name"]}', 'success')
            
            # Update progress
            progress = 30 + (60 * (idx + 1) / total_pages)
            scraping_status['progress'] = progress
        
        scraping_status['progress'] = 90
        scraping_status['status_message'] = 'Saving data...'
        
        # Save results
        scraper.save_to_csv('static/alstapingtools_products.csv')
        scraper.save_to_json('static/alstapingtools_products.json')
        scraper.generate_report()
        
        scraping_status['progress'] = 100
        scraping_status['status_message'] = 'Complete!'
        add_log(f'Scraping complete! Found {len(scraper.products)} products', 'success')
        
    except Exception as e:
        add_log(f'Error: {str(e)}', 'error')
        logger.error(f"Scraping error: {e}", exc_info=True)
    finally:
        scraping_status['is_running'] = False

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('scraper_app.html')

@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping already in progress'}), 400
    
    data = request.json
    url = data.get('url', 'http://alstapingtools.com')
    delay = float(data.get('delay', 1.5))
    download_images = data.get('download_images', True)
    
    # Start scraping in a background thread
    thread = threading.Thread(
        target=run_scraper_thread,
        args=(url, delay, download_images)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started', 'status': 'success'})

@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/products')
def get_products():
    """Get scraped products"""
    global scraper
    if scraper and scraper.products:
        return jsonify({'products': scraper.products})
    return jsonify({'products': []})

@app.route('/api/download/<file_type>')
def download_file(file_type):
    """Download scraped data files"""
    file_map = {
        'csv': 'static/alstapingtools_products.csv',
        'json': 'static/alstapingtools_products.json',
        'report': 'scrape_report.txt'
    }
    
    if file_type not in file_map:
        return jsonify({'error': 'Invalid file type'}), 400
    
    file_path = file_map[file_type]
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    print("=" * 80)
    print("AlsTapingTools.com Scraper Web Application")
    print("=" * 80)
    print()
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
