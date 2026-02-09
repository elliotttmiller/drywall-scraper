#!/usr/bin/env python3
"""
ALS Taping Tools Complete Product Scraper
Extracts: Product Name, Description, SKU, Price, Multiple Images
Output: Structured CSV/JSON catalog
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

# Configuration
BASE_URL = "https://www.alstapingtools.com"
START_URL = "https://www.alstapingtools.com/shop-by-product/?mode=4&sort=alphaasc&limit=100"
OUTPUT_CSV = "als_taping_tools_catalog.csv"
OUTPUT_JSON = "als_taping_tools_catalog.json"
PROGRESS_FILE = "als_scraper_progress.json"
DELAY = 2.0  # seconds between requests

def get_page(url, retries=3):
    """Fetch page with error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ⚠ Attempt {attempt + 1}/{retries} failed: {str(e)[:80]}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None

def extract_product_links(html):
    """Extract all product URLs from listing page"""
    soup = BeautifulSoup(html, 'html.parser')
    products = []

    # Strategy: only accept anchors that look like product links in listing pages.
    # Heuristics used:
    # - Anchor contains an <img> whose src includes '/products/' (product images)
    # - href is an absolute or site-relative URL that points to a top-level slug (e.g. /my-product/)
    # - exclude known non-product paths (brands, shop-by-product listing, parts, cart, etc.)
    seen = set()

    anchors = soup.find_all('a', href=True)
    for a in anchors:
        href = a.get('href')
        if not href:
            continue

        # Skip anchors that clearly are not product links
        if any(skip in href for skip in ['cart.php', 'compare', '/login', '/wishlist', 'javascript:', 'mailto:']):
            continue

        # Only consider anchors that contain a product image or image-like thumbnail
        img = a.find('img')
        if not img:
            # also allow anchors whose parent contains an image (some themes wrap links)
            parent_img = a.find_parent().find('img') if a.find_parent() else None
            if not parent_img:
                continue
            img = parent_img

        src = img.get('src') or ''
        if '/products/' not in src and 'product' not in src.lower():
            # Not a product image
            continue

        # Build absolute URL
        if href.startswith('/'):
            url = urljoin(BASE_URL, href)
        elif href.startswith(BASE_URL):
            url = href
        else:
            # Ignore third-party links or javascript anchors
            continue

        # Normalize (remove fragments)
        url = url.split('#')[0]

        # Exclude listing and non-product paths explicitly
        if any(skip in url for skip in ['/shop-by-product', '/brands', '/order-parts', '/login', '/cart', '/compare', '/wishlist', '/category/']):
            continue

        # Ensure it's a top-level product slug: one path component (e.g. https://.../my-product/)
        path = urlparse(url).path.strip('/')
        if not path:
            continue
        parts = path.split('/')
        if len(parts) != 1:
            # If it's nested (category/product), skip. We only want direct product pages.
            continue

        # Common slug sanity: not all digits and at least 4 chars
        slug = parts[0]
        if slug.isdigit() or len(slug) < 4:
            continue

        # Must end with slash on this site
        if not url.endswith('/'):
            url = url + '/'

        # De-duplicate and collect
        if url not in seen:
            products.append(url)
            seen.add(url)

    return products

def find_max_listing_page(html):
    """Scan listing page HTML and return the maximum page number found in pagination.

    If no pagination is found, returns 1.
    """
    soup = BeautifulSoup(html, 'html.parser')
    page_links = soup.find_all('a', href=re.compile(r'[?&]page=\d+'))
    max_page = 1
    for link in page_links:
        href = link.get('href', '')
        m = re.search(r'[?&]page=(\d+)', href)
        if m:
            try:
                p = int(m.group(1))
                max_page = max(max_page, p)
            except:
                continue
    # Also consider numbered pagination elements (plain numbers)
    if max_page == 1:
        pagination = soup.find(['nav', 'ul', 'div'], class_=re.compile(r'paginat|pagination|paging', re.I))
        if pagination:
            nums = pagination.find_all(text=re.compile(r'^\d+$'))
            for t in nums:
                try:
                    p = int(t.strip())
                    max_page = max(max_page, p)
                except:
                    pass
    return max_page

def build_listing_page_url(base_url, page_num):
    """Return a page URL for the given page number based on the START_URL/query params."""
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs['page'] = [str(page_num)]
    new_q = urlencode(qs, doseq=True)
    new_parsed = parsed._replace(query=new_q)
    return urlunparse(new_parsed)

def check_pagination(html):
    """Check if there's a next page and return URL"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for pagination links
    next_link = soup.find('a', string=re.compile(r'Next|›|»', re.I))
    if next_link and next_link.get('href'):
        href = next_link.get('href')
        if href.startswith('http'):
            return href  # Absolute URL
        else:
            return urljoin(BASE_URL, href)  # Relative URL
    
    # Check for numbered pagination - look for links with page parameter
    page_links = soup.find_all('a', href=re.compile(r'[?&]page=\d+'))
    if page_links:
        current_page = 1
        max_page = 1
        
        for link in page_links:
            href = link.get('href', '')
            # Extract page number
            match = re.search(r'[?&]page=(\d+)', href)
            if match:
                page_num = int(match.group(1))
                max_page = max(max_page, page_num)
        
        # If we're on page 1 and there are more pages, return page 2
        if max_page > 1:
            next_url = START_URL
            if '?' in next_url:
                next_url += '&page=2'
            else:
                next_url += '?page=2'
            return next_url
    
    return None

def extract_product_details(url):
    """Extract complete product information from product page"""
    html = get_page(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    product = {
        'url': url,
        'name': '',
        'sku': '',
        'upc': '',
        'mpn': '',
        'brand': '',
        'price': '',
        'price_numeric': None,
        'description_short': '',
        'description_full': '',
        'specifications': {},
        'in_stock': False,
        'images': [],
        'category': '',
        'manufacturer': ''
    }
    
    # Extract product name
    # Extract product name (explicit selector from site)
    name_elem = soup.find('h1', class_=re.compile(r'productView-title', re.I))
    if not name_elem:
        name_elem = soup.find('h1', class_=re.compile(r'product|title', re.I))
    if not name_elem:
        name_elem = soup.find('h1')
    if name_elem:
        product['name'] = name_elem.get_text(strip=True)

    # SKU / UPC / MPN are in the productView-info dl (per provided source)
    # SKU / UPC / MPN are in the productView-info dd (per provided source)
    sku_dd = soup.find('dd', class_=re.compile(r'productView-info-value--sku', re.I))
    if sku_dd:
        # Prefer data attribute if present, otherwise visible text
        sku_attr = sku_dd.get('data-product-sku')
        if sku_attr and sku_attr.strip():
            product['sku'] = sku_attr.strip()
        else:
            product['sku'] = sku_dd.get_text(strip=True)

    upc_dd = soup.find('dd', class_=re.compile(r'productView-info-value--upc', re.I))
    if upc_dd:
        upc_attr = upc_dd.get('data-product-upc')
        if upc_attr and upc_attr.strip():
            product['upc'] = upc_attr.strip()
        else:
            product['upc'] = upc_dd.get_text(strip=True)

    mpn_dd = soup.find('dd', class_=re.compile(r'productView-info-value--mpn', re.I))
    if mpn_dd:
        mpn_attr = mpn_dd.get('data-product-mpn') or mpn_dd.get('data-original-mpn')
        if mpn_attr and mpn_attr.strip():
            product['mpn'] = mpn_attr.strip()
        else:
            product['mpn'] = mpn_dd.get_text(strip=True)
    
    # Extract price (explicit price--main span)
    price_elem = soup.find('span', class_=re.compile(r'price--main|price\-\-main', re.I))
    if not price_elem:
        # fallback to any price-like span/div
        price_elem = soup.find(['span', 'div'], class_=re.compile(r'price', re.I))
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        product['price'] = price_text
        # Extract numeric value
        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
        if price_match:
            try:
                product['price_numeric'] = float(price_match.group(1).replace(',', ''))
            except:
                pass
    
    # Extract brand/manufacturer per provided HTML: h5.productView-brand > a
    brand_elem = soup.find('h5', class_=re.compile(r'productView-brand', re.I))
    if brand_elem:
        a = brand_elem.find('a')
        if a:
            product['brand'] = a.get_text(strip=True)
            product['manufacturer'] = product['brand']
    
    # Extract stock status
    stock_elem = soup.find(text=re.compile(r'In Stock|Out of stock', re.I))
    if stock_elem:
        product['in_stock'] = 'in stock' in stock_elem.lower()
    
    # Extract full description using the provided selector
    desc_section = soup.find('div', class_=re.compile(r'productView-description-tabContent', re.I))
    if not desc_section:
        # fallback to common description containers
        desc_section = soup.find('div', {'id': 'tab-description'})
        if not desc_section:
            desc_section = soup.find(['div', 'section'], class_=re.compile(r'description|detail', re.I))

    if desc_section:
        # Remove script and style tags
        for tag in desc_section.find_all(['script', 'style']):
            tag.decompose()
        product['description_full'] = desc_section.get_text(separator='\n\n', strip=True)
        # short description = first paragraph of full
        first_para = desc_section.find('p')
        if first_para:
            product['description_short'] = first_para.get_text(strip=True)[:500]
        else:
            product['description_short'] = product['description_full'][:500]
    
    # Extract specifications from table
    spec_section = soup.find('div', {'id': 'tab-addition'})
    if spec_section:
        # Look for table or definition list
        table = spec_section.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        product['specifications'][key] = value
    
    # Extract ALL images - primary and gallery
    images = []
    
    # Primary image
    main_img = soup.find('img', class_=re.compile(r'product.*image|main', re.I))
    if main_img and main_img.get('src'):
        img_url = urljoin(BASE_URL, main_img['src'])
        # Get high-res version
        img_url = img_url.replace('/stencil/608x608/', '/stencil/1280x1280/')
        img_url = img_url.replace('/stencil/80x80/', '/stencil/1280x1280/')
        images.append(img_url)
    
    # Gallery images
    gallery = soup.find_all('a', href=re.compile(r'\.jpg|\.png', re.I))
    for img_link in gallery:
        href = img_link.get('href')
        if href and 'products/' in href:
            img_url = urljoin(BASE_URL, href)
            if img_url not in images:
                images.append(img_url)
    
    # Thumbnail images
    thumbnails = soup.find_all('img', src=re.compile(r'/products/\d+/'))
    for thumb in thumbnails:
        src = thumb.get('src')
        if src:
            # Convert to high-res
            img_url = urljoin(BASE_URL, src)
            img_url = re.sub(r'/stencil/\d+x\d+/', '/stencil/1280x1280/', img_url)
            if img_url not in images and '1280x1280' in img_url:
                images.append(img_url)
    
    product['images'] = images
    
    # Extract category from breadcrumb or URL
    breadcrumb = soup.find(['nav', 'div'], class_=re.compile(r'breadcrumb', re.I))
    if breadcrumb:
        links = breadcrumb.find_all('a')
        if len(links) > 1:
            product['category'] = links[-1].get_text(strip=True)
    
    return product

def check_pagination(html):
    """Check if there's a next page and return URL"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for pagination links
    next_link = soup.find('a', string=re.compile(r'Next|›|»', re.I))
    if next_link and next_link.get('href'):
        return urljoin(BASE_URL, next_link['href'])
    
    # Check for numbered pagination
    pagination = soup.find(['nav', 'div'], class_=re.compile(r'paginat', re.I))
    if pagination:
        links = pagination.find_all('a', href=True)
        current_page = None
        for i, link in enumerate(links):
            if 'active' in link.get('class', []) or 'current' in link.get('class', []):
                # Found current page, get next
                if i + 1 < len(links):
                    next_page = links[i + 1].get('href')
                    if next_page and 'page=' in next_page:
                        return urljoin(BASE_URL, next_page)
    
    return None

def save_progress(data):
    """Save progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_progress():
    """Load progress"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'completed_urls': [], 'last_listing_page': START_URL}

def main():
    print("=" * 80)
    print("ALS TAPING TOOLS - COMPLETE PRODUCT SCRAPER")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Output JSON: {OUTPUT_JSON}")
    print("=" * 80)
    
    all_products = []
    progress = load_progress()
    
    # Step 1: Collect all product URLs from all pages
    print("\n[1/2] Collecting product URLs from all listing pages...")
    product_urls = []

    # Fetch first listing page and detect how many pages exist
    print(f"\n  Page 1: {START_URL}")
    first_html = get_page(START_URL)
    if not first_html:
        print("  ✗ Failed to fetch first listing page")
        return

    max_page = find_max_listing_page(first_html)
    print(f"  ✓ Detected {max_page} listing pages")

    # Build all listing page URLs and iterate them deterministically
    listing_pages = [build_listing_page_url(START_URL, p) for p in range(1, max_page + 1)]
    for page_num, page_url in enumerate(listing_pages, start=1):
        print(f"\n  Page {page_num}: {page_url}")
        html = first_html if page_num == 1 else get_page(page_url)
        if not html:
            print(f"  ✗ Failed to fetch page {page_num}: {page_url}")
            continue

        # Extract product links
        links = extract_product_links(html)
        new_links = [l for l in links if l not in product_urls]
        product_urls.extend(new_links)
        print(f"  ✓ Found {len(new_links)} products on page {page_num} (Total: {len(product_urls)})")
        time.sleep(DELAY)

    print(f"\n  ✓ Completed listing pages iteration")
    
    print(f"\n✓ Total products to scrape: {len(product_urls)}")
    
    # Step 2: Scrape each product (stream results live to CSV and JSONL)
    print(f"\n[2/2] Scraping detailed product information... (streaming to disk)")
    print("=" * 80)

    # Prepare CSV writer and JSONL streaming file
    fieldnames = [
        'name', 'sku', 'upc', 'mpn', 'brand', 'manufacturer', 'price', 'price_numeric',
        'in_stock', 'category', 'description_short', 'description_full',
        'url', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
        'image_6', 'image_7', 'image_8', 'image_9', 'all_images',
        'specifications_json'
    ]

    # Open CSV and JSONL for streaming writes
    csv_f = open(OUTPUT_CSV, 'w', newline='', encoding='utf-8')
    csv_writer = csv.DictWriter(csv_f, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_f.flush()

    # JSONL file holds one JSON object per line for live streaming
    OUTPUT_JSONL = OUTPUT_JSON.replace('.json', '.jsonl') if OUTPUT_JSON.endswith('.json') else OUTPUT_JSON + '.jsonl'
    jsonl_f = open(OUTPUT_JSONL, 'w', encoding='utf-8')

    def flush_to_disk(fhandle):
        try:
            fhandle.flush()
            import os
            os.fsync(fhandle.fileno())
        except Exception:
            pass

    for i, url in enumerate(product_urls, 1):
        # Skip if already completed
        if url in progress.get('completed_urls', []):
            print(f"[{i}/{len(product_urls)}] Skipping (already done): {url}")
            continue
        
        print(f"\n[{i}/{len(product_urls)}] Scraping: {url}")
        
        product = extract_product_details(url)
        
        if product:
            all_products.append(product)
            print(f"  ✓ Name: {product['name'][:60]}")
            print(f"  ✓ SKU: {product['sku']}")
            print(f"  ✓ UPC: {product['upc']}")
            print(f"  ✓ Price: {product['price']}")
            print(f"  ✓ Images: {len(product['images'])}")
            print(f"  ✓ Brand: {product['brand']}")

            # Build CSV row
            row = {
                'name': product['name'],
                'sku': product['sku'],
                'upc': product['upc'],
                'mpn': product['mpn'],
                'brand': product['brand'],
                'manufacturer': product['manufacturer'],
                'price': product['price'],
                'price_numeric': product['price_numeric'],
                'in_stock': product['in_stock'],
                'category': product['category'],
                'description_short': product['description_short'],
                'description_full': product['description_full'],
                'url': product['url'],
                'specifications_json': json.dumps(product['specifications']) if product['specifications'] else ''
            }
            for idx in range(9):
                row[f'image_{idx+1}'] = product['images'][idx] if idx < len(product['images']) else ''
            row['all_images'] = '|'.join(product['images'])

            try:
                csv_writer.writerow(row)
                flush_to_disk(csv_f)
            except Exception as e:
                print(f"  ⚠ Failed to write CSV row: {e}")

            # Write JSONL line
            try:
                jsonl_f.write(json.dumps(product, ensure_ascii=False) + '\n')
                flush_to_disk(jsonl_f)
            except Exception as e:
                print(f"  ⚠ Failed to write JSONL: {e}")

            # Save progress (per-product)
            progress['completed_urls'].append(url)
            save_progress(progress)
        else:
            print(f"  ✗ Failed to extract product data")

        time.sleep(DELAY)

    # Close streaming files
    try:
        csv_f.close()
    except:
        pass
    try:
        jsonl_f.close()
    except:
        pass

    # Optionally produce final pretty JSON array from JSONL for compatibility
    try:
        final_products = []
        with open(OUTPUT_JSONL, 'r', encoding='utf-8') as jfh:
            for line in jfh:
                line = line.strip()
                if not line:
                    continue
                try:
                    final_products.append(json.loads(line))
                except:
                    pass
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as fj:
            json.dump(final_products, fj, indent=2, ensure_ascii=False)
        print(f"\n✓ Final JSON saved: {OUTPUT_JSON} (generated from {OUTPUT_JSONL})")
    except Exception as e:
        print(f"\n⚠ Failed to generate final JSON: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("SCRAPING COMPLETE!")
    print("=" * 80)
    print(f"Total products scraped: {len(all_products)}")
    print(f"Products with images: {sum(1 for p in all_products if p['images'])}")
    print(f"Products with prices: {sum(1 for p in all_products if p['price'])}")
    print(f"Products in stock: {sum(1 for p in all_products if p['in_stock'])}")
    if all_products:
        print(f"Average images per product: {sum(len(p['images']) for p in all_products) / len(all_products):.1f}")
    else:
        print("Average images per product: N/A (no products found)")
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_CSV} (streamed)")
    print(f"  - {OUTPUT_JSONL} (streamed, newline-delimited JSON)")
    print(f"  - {OUTPUT_JSON} (final pretty JSON generated from JSONL)")
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
