#!/usr/bin/env python3
"""
Comprehensive Web Scraper for AlsTapingTools.com
Extracts ALL products: name, description, price, SKU, and images from entire website
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Set, Optional
import re
from datetime import datetime
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlsTapingToolsScraper:
    """Comprehensive scraper for AlsTapingTools.com"""
    
    def __init__(self, base_url: str = "http://alstapingtools.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.visited_urls: Set[str] = set()
        self.product_urls: Set[str] = set()
        self.products: List[Dict] = []
        self.delay = 1.5  # Delay between requests (respectful scraping)
        self.timeout = 30
        self.image_folder = "product_images"
        
        # Create image folder
        Path(self.image_folder).mkdir(exist_ok=True)
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                time.sleep(self.delay)
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.warning(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * 2)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
        return None
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent comparison"""
        parsed = urlparse(url)
        # Remove fragments and normalize
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the target domain"""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc or parsed.netloc == ''
    
    def discover_all_pages(self) -> Set[str]:
        """Discover all pages on the website through crawling"""
        pages_to_visit = {self.base_url}
        all_pages = set()
        
        logger.info("Starting website crawl to discover all pages...")
        
        while pages_to_visit:
            current_url = pages_to_visit.pop()
            
            if current_url in all_pages:
                continue
                
            all_pages.add(current_url)
            logger.info(f"Crawling: {current_url} (Total pages found: {len(all_pages)})")
            
            soup = self.get_page(current_url)
            if not soup:
                continue
            
            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                normalized_url = self.normalize_url(full_url)
                
                if self.is_valid_url(normalized_url) and normalized_url not in all_pages:
                    pages_to_visit.add(normalized_url)
        
        logger.info(f"Crawl complete! Found {len(all_pages)} total pages")
        return all_pages
    
    def is_product_page(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if a page is a product page"""
        # Common indicators of product pages
        indicators = [
            soup.find(class_=re.compile(r'product', re.I)),
            soup.find(id=re.compile(r'product', re.I)),
            soup.find(attrs={'itemtype': re.compile(r'Product', re.I)}),
            soup.find(class_=re.compile(r'price', re.I)),
            soup.find(class_=re.compile(r'sku', re.I)),
            soup.find('meta', attrs={'property': 'og:type', 'content': 'product'}),
            'product' in url.lower(),
            '/p/' in url.lower(),
            '/item/' in url.lower(),
        ]
        
        return any(indicators)
    
    def extract_price(self, soup: BeautifulSoup) -> str:
        """Extract price from product page using multiple strategies"""
        price_selectors = [
            ('class', re.compile(r'price|cost|amount', re.I)),
            ('id', re.compile(r'price|cost', re.I)),
            ('itemprop', 'price'),
            ('data-price', True),
        ]
        
        for selector_type, selector_value in price_selectors:
            if selector_type == 'class':
                elements = soup.find_all(class_=selector_value)
            elif selector_type == 'id':
                elements = soup.find_all(id=selector_value)
            elif selector_type == 'itemprop':
                elements = soup.find_all(attrs={'itemprop': selector_value})
            elif selector_type == 'data-price':
                elements = soup.find_all(attrs={'data-price': True})
            else:
                elements = []
            
            for element in elements:
                text = element.get_text(strip=True)
                # Look for price patterns
                price_match = re.search(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                if price_match:
                    return price_match.group(0).strip()
        
        # Check meta tags
        meta_price = soup.find('meta', attrs={'property': 'og:price:amount'})
        if meta_price and meta_price.get('content'):
            return f"${meta_price['content']}"
        
        return "N/A"
    
    def extract_sku(self, soup: BeautifulSoup) -> str:
        """Extract SKU from product page"""
        sku_selectors = [
            ('class', re.compile(r'sku|product-code|item-number|model', re.I)),
            ('id', re.compile(r'sku|product-code', re.I)),
            ('itemprop', 'sku'),
            ('data-sku', True),
        ]
        
        for selector_type, selector_value in sku_selectors:
            if selector_type == 'class':
                element = soup.find(class_=selector_value)
            elif selector_type == 'id':
                element = soup.find(id=selector_value)
            elif selector_type == 'itemprop':
                element = soup.find(attrs={'itemprop': selector_value})
            elif selector_type == 'data-sku':
                element = soup.find(attrs={'data-sku': True})
                if element:
                    return element.get('data-sku', 'N/A')
                continue
            else:
                element = None
            
            if element:
                text = element.get_text(strip=True)
                # Clean up SKU
                sku = re.sub(r'SKU:?\s*', '', text, flags=re.I).strip()
                if sku:
                    return sku
        
        return "N/A"
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        desc_selectors = [
            ('class', re.compile(r'description|details|product-info', re.I)),
            ('id', re.compile(r'description|details', re.I)),
            ('itemprop', 'description'),
        ]
        
        for selector_type, selector_value in desc_selectors:
            if selector_type == 'class':
                element = soup.find(class_=selector_value)
            elif selector_type == 'id':
                element = soup.find(id=selector_value)
            elif selector_type == 'itemprop':
                element = soup.find(attrs={'itemprop': selector_value})
            else:
                element = None
            
            if element:
                # Get text but preserve some structure
                text = element.get_text(separator=' ', strip=True)
                # Clean up excessive whitespace
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 20:  # Ensure it's substantial
                    return text[:1000]  # Limit length
        
        # Fallback to meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        return "N/A"
    
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name/title"""
        # Try h1 tags first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try title tag
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            # Clean up common suffixes
            title_text = re.sub(r'\s*[-|]\s*.*$', '', title_text)
            return title_text
        
        # Try product name classes
        name_element = soup.find(class_=re.compile(r'product-name|product-title', re.I))
        if name_element:
            return name_element.get_text(strip=True)
        
        return "N/A"
    
    def extract_images(self, soup: BeautifulSoup, product_name: str) -> List[str]:
        """Extract all product images"""
        images = []
        image_urls = set()
        
        # Find images in various ways
        image_selectors = [
            soup.find_all('img', class_=re.compile(r'product|item|gallery', re.I)),
            soup.find_all('img', itemprop='image'),
            soup.find_all('img', attrs={'data-zoom': True}),
            soup.find_all('img', attrs={'data-src': True}),
            soup.find_all('a', attrs={'data-image': True}),
        ]
        
        for selector_result in image_selectors:
            for element in selector_result:
                # Get image URL from various attributes
                img_url = None
                if element.name == 'img':
                    img_url = element.get('src') or element.get('data-src') or element.get('data-original')
                elif element.name == 'a':
                    img_url = element.get('data-image') or element.get('href')
                
                if img_url:
                    # Convert to absolute URL
                    full_url = urljoin(self.base_url, img_url)
                    # Avoid duplicates and tiny images
                    if full_url not in image_urls and not any(x in full_url.lower() for x in ['logo', 'icon', 'thumb']):
                        image_urls.add(full_url)
                        images.append(full_url)
        
        # Also check Open Graph image
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image and og_image.get('content'):
            og_url = urljoin(self.base_url, og_image['content'])
            if og_url not in image_urls:
                images.append(og_url)
        
        return images
    
    def download_image(self, image_url: str, product_name: str, index: int = 0) -> str:
        """Download product image to local folder"""
        try:
            response = self.session.get(image_url, timeout=15)
            response.raise_for_status()
            
            # Generate filename
            ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
            safe_name = re.sub(r'[^\w\s-]', '', product_name)[:50]
            filename = f"{safe_name}_{index}{ext}"
            filepath = os.path.join(self.image_folder, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return filepath
        except Exception as e:
            logger.warning(f"Failed to download image {image_url}: {e}")
            return image_url
    
    def extract_product_data(self, url: str) -> Optional[Dict]:
        """Extract all product data from a product page"""
        soup = self.get_page(url)
        if not soup:
            return None
        
        # Verify it's a product page
        if not self.is_product_page(soup, url):
            return None
        
        logger.info(f"Extracting product data from: {url}")
        
        # Extract all data
        product_name = self.extract_product_name(soup)
        price = self.extract_price(soup)
        sku = self.extract_sku(soup)
        description = self.extract_description(soup)
        image_urls = self.extract_images(soup, product_name)
        
        # Download images (optional - can be toggled)
        local_images = []
        for idx, img_url in enumerate(image_urls[:5]):  # Limit to 5 images per product
            local_path = self.download_image(img_url, product_name, idx)
            local_images.append(local_path)
        
        product_data = {
            'product_name': product_name,
            'sku': sku,
            'price': price,
            'description': description,
            'url': url,
            'image_urls': '|'.join(image_urls),
            'local_images': '|'.join(local_images),
            'image_count': len(image_urls),
            'scraped_at': datetime.now().isoformat()
        }
        
        return product_data
    
    def scrape_all_products(self) -> List[Dict]:
        """Main method to scrape all products from the entire website"""
        logger.info("=" * 80)
        logger.info("Starting comprehensive scrape of AlsTapingTools.com")
        logger.info("=" * 80)
        
        # Step 1: Discover all pages
        all_pages = self.discover_all_pages()
        
        # Step 2: Filter and scrape product pages
        logger.info("Identifying and scraping product pages...")
        for page_url in all_pages:
            if page_url in self.visited_urls:
                continue
            
            self.visited_urls.add(page_url)
            product_data = self.extract_product_data(page_url)
            
            if product_data:
                self.products.append(product_data)
                logger.info(f"Product extracted: {product_data['product_name']} (Total: {len(self.products)})")
        
        logger.info("=" * 80)
        logger.info(f"Scraping complete! Total products found: {len(self.products)}")
        logger.info("=" * 80)
        
        return self.products
    
    def save_to_csv(self, filename: str = 'products.csv'):
        """Save products to CSV file"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        fieldnames = ['product_name', 'sku', 'price', 'description', 'url', 
                      'image_urls', 'local_images', 'image_count', 'scraped_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        
        logger.info(f"Products saved to {filename}")
    
    def save_to_json(self, filename: str = 'products.json'):
        """Save products to JSON file"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.products, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Products saved to {filename}")
    
    def generate_report(self):
        """Generate a summary report"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           SCRAPING REPORT - AlsTapingTools.com              ║
╚══════════════════════════════════════════════════════════════╝

Total Products Found: {len(self.products)}
Total Pages Visited: {len(self.visited_urls)}
Total Images Downloaded: {sum(p.get('image_count', 0) for p in self.products)}

Products with SKU: {sum(1 for p in self.products if p.get('sku') != 'N/A')}
Products with Price: {sum(1 for p in self.products if p.get('price') != 'N/A')}
Products with Description: {sum(1 for p in self.products if p.get('description') != 'N/A')}
Products with Images: {sum(1 for p in self.products if p.get('image_count', 0) > 0)}

Scrape completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        print(report)
        
        with open('scrape_report.txt', 'w') as f:
            f.write(report)

def main():
    """Main execution function"""
    print("=" * 80)
    print("AlsTapingTools.com Comprehensive Product Scraper")
    print("=" * 80)
    print()
    
    # Initialize scraper
    scraper = AlsTapingToolsScraper()
    
    # Scrape all products
    products = scraper.scrape_all_products()
    
    # Save results
    scraper.save_to_csv('alstapingtools_products.csv')
    scraper.save_to_json('alstapingtools_products.json')
    
    # Generate report
    scraper.generate_report()
    
    print()
    print("✓ Scraping completed successfully!")
    print(f"✓ Found {len(products)} products")
    print("✓ Data saved to: alstapingtools_products.csv")
    print("✓ Data saved to: alstapingtools_products.json")
    print(f"✓ Images saved to: {scraper.image_folder}/")
    print()

if __name__ == "__main__":
    main()
