#!/usr/bin/env python3
"""
TSW Fast Complete Product Scraper
Scrapes ALL products with detailed specifications from tswfast.com
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
import json
from datetime import datetime

# Configuration
BASE_URL = "https://www.tswfast.com"
SHOP_BY_BRAND_URL = "https://www.tswfast.com/category/tools_shop_by_brand"
OUTPUT_FILE = "/mnt/user-data/outputs/tswfast_all_products.csv"
PROGRESS_FILE = "/home/claude/scraper_progress.json"
DELAY_BETWEEN_REQUESTS = 1.5  # seconds

def get_page(url, retries=3):
    """Fetch page with retries and error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ⚠ Attempt {attempt + 1}/{retries} failed: {str(e)[:100]}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None
    return None

def extract_brand_urls(html):
    """Extract all brand category URLs"""
    soup = BeautifulSoup(html, 'html.parser')
    brands = []
    seen = set()
    
    # Find all links matching brand pattern
    links = soup.find_all('a', href=re.compile(r'/category/brand_|/category/radians'))
    
    for link in links:
        href = link.get('href')
        url = urljoin(BASE_URL, href)
        
        if url not in seen:
            name = link.get_text(strip=True)
            if name:  # Only add if has a name
                brands.append({'name': name, 'url': url})
                seen.add(url)
    
    return brands

def extract_product_details(product_url):
    """Fetch individual product page for detailed specs"""
    html = get_page(product_url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    details = {}
    
    # Extract specifications table if exists
    spec_tables = soup.find_all(['table', 'dl'], class_=re.compile(r'spec|attribute|detail', re.I))
    
    for table in spec_tables:
        if table.name == 'table':
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        details[key] = value
        elif table.name == 'dl':
            dts = table.find_all('dt')
            dds = table.find_all('dd')
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and value:
                    details[key] = value
    
    # Extract description
    desc_selectors = [
        ('div', {'class': re.compile(r'description|detail|content', re.I)}),
        ('div', {'id': re.compile(r'description|detail', re.I)}),
        ('p', {'class': re.compile(r'description', re.I)})
    ]
    
    for tag, attrs in desc_selectors:
        desc_elem = soup.find(tag, attrs)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if len(desc_text) > 20:  # Only if substantial
                details['full_description'] = desc_text
                break
    
    return details

def extract_products_from_brand_page(html, brand_name):
    """Extract all products from a brand page"""
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # Find all product links
    product_links = soup.find_all('a', href=re.compile(r'/product/[^/]+'))
    
    seen_urls = set()
    
    for link in product_links:
        url = urljoin(BASE_URL, link.get('href'))
        
        # Skip duplicates and non-product links
        if url in seen_urls or '?' in url:
            continue
        seen_urls.add(url)
        
        # Get product name
        name = link.get_text(strip=True)
        
        # If no text, try img alt
        if not name or len(name) < 3:
            img = link.find('img')
            if img and img.get('alt'):
                name = img.get('alt').strip()
        
        if not name or len(name) < 3:
            continue
        
        # Find container for additional info
        container = link.find_parent(['div', 'li', 'article'])
        
        product = {
            'brand': brand_name,
            'product_name': name,
            'part_number': '',
            'url': url,
            'image_url': '',
            'short_description': '',
            'category': ''
        }
        
        if container:
            # Extract part number
            part_pattern = re.compile(r'\bPart\s*\n?\s*([A-Z0-9-]+)', re.I)
            container_text = container.get_text()
            part_match = part_pattern.search(container_text)
            if part_match:
                product['part_number'] = part_match.group(1)
            
            # Extract image
            img = container.find('img')
            if img and img.get('src'):
                src = img.get('src')
                if 'blank' not in src.lower() and '1x1' not in src:
                    product['image_url'] = urljoin(BASE_URL, src)
        
        products.append(product)
    
    return products

def check_pagination(html):
    """Check if there are more pages and return next page URL"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for pagination indicators
    # Common patterns: "Next", "→", page numbers, etc.
    next_links = soup.find_all('a', text=re.compile(r'Next|next|→|»', re.I))
    
    for link in next_links:
        href = link.get('href')
        if href and 'page' in href.lower():
            return urljoin(BASE_URL, href)
    
    # Look for numbered pagination
    page_links = soup.find_all('a', href=re.compile(r'[?&]page=\d+', re.I))
    if page_links:
        # Get the last page number to see if there are more
        return None  # For now, assume single page per brand
    
    return None

def save_progress(data):
    """Save progress to JSON file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_progress():
    """Load progress from JSON file"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'brands_completed': [], 'last_brand_index': 0}

def scrape_all_products(get_detailed_specs=False):
    """Main scraping function"""
    print("=" * 80)
    print("TSW FAST COMPLETE PRODUCT SCRAPER")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Detailed specs: {'YES - Will visit each product page' if get_detailed_specs else 'NO - Quick scrape only'}")
    print("=" * 80)
    
    # Step 1: Get all brands
    print("\n[1/3] Fetching brand list...")
    html = get_page(SHOP_BY_BRAND_URL)
    if not html:
        print("❌ Failed to fetch brand page. Exiting.")
        return
    
    brands = extract_brand_urls(html)
    print(f"✓ Found {len(brands)} brands")
    
    # Load progress
    progress = load_progress()
    start_index = progress.get('last_brand_index', 0)
    
    if start_index > 0:
        print(f"📝 Resuming from brand #{start_index + 1}")
    
    # Step 2: Scrape each brand
    print(f"\n[2/3] Scraping products from {len(brands)} brands...")
    all_products = []
    
    # Open CSV file and write incrementally
    csv_file = open(OUTPUT_FILE, 'w', newline='', encoding='utf-8')
    fieldnames = [
        'brand', 'product_name', 'part_number', 'url', 'image_url', 
        'short_description', 'category', 'specifications'
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    total_products = 0
    
    try:
        for i, brand in enumerate(brands[start_index:], start=start_index):
            brand_name = brand['name']
            brand_url = brand['url']
            
            print(f"\n[{i+1}/{len(brands)}] {brand_name}")
            print(f"  URL: {brand_url}")
            
            # Fetch brand page
            html = get_page(brand_url)
            if not html:
                print(f"  ⚠ Failed to fetch, skipping...")
                continue
            
            # Extract products
            products = extract_products_from_brand_page(html, brand_name)
            print(f"  ✓ Found {len(products)} products")
            
            # Get detailed specs if requested
            if get_detailed_specs and len(products) <= 50:  # Only for smaller brands
                print(f"  📋 Fetching detailed specifications...")
                for j, product in enumerate(products, 1):
                    if j % 10 == 0:
                        print(f"    Progress: {j}/{len(products)}")
                    
                    details = extract_product_details(product['url'])
                    if details:
                        product['specifications'] = json.dumps(details)
                    
                    time.sleep(DELAY_BETWEEN_REQUESTS * 0.5)
            else:
                for product in products:
                    product['specifications'] = ''
            
            # Write to CSV immediately
            writer.writerows(products)
            csv_file.flush()  # Force write to disk
            
            total_products += len(products)
            
            # Update progress
            progress['last_brand_index'] = i + 1
            progress['brands_completed'].append(brand_name)
            save_progress(progress)
            
            # Rate limiting
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    finally:
        csv_file.close()
    
    # Step 3: Summary
    print("\n" + "=" * 80)
    print("SCRAPING COMPLETE!")
    print("=" * 80)
    print(f"Total brands scraped: {len(progress['brands_completed'])}")
    print(f"Total products extracted: {total_products}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    # Set to True to visit each product page for detailed specs (much slower)
    # Set to False for quick scrape of all products
    GET_DETAILED_SPECS = False
    
    scrape_all_products(get_detailed_specs=GET_DETAILED_SPECS)
