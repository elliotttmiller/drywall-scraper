# ALS Taping Tools Complete Product Scraper

Comprehensive web scraper for extracting ALL product data from alstapingtools.com including names, descriptions, SKUs, prices, and multiple images for every product.

## What This Scraper Does

Extracts complete product catalogs from ALS Taping Tools website:
- ✅ Product names
- ✅ SKUs, UPCs, MPNs
- ✅ Prices (with numeric values)
- ✅ Full descriptions
- ✅ Product specifications
- ✅ ALL product images (up to 9 per product, high-resolution)
- ✅ Brand/manufacturer information
- ✅ Stock status
- ✅ Product categories
- ✅ Product URLs

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Run the scraper
python3 als_taping_tools_scraper.py
```

The scraper will:
1. Discover all product listing pages
2. Extract all product URLs
3. Visit each product page for detailed information
4. Save to both CSV and JSON formats

## Output Files

### CSV Format (`als_taping_tools_catalog.csv`)
Structured spreadsheet with columns:
- `name` - Product name
- `sku` - Product SKU/Part number
- `upc` - UPC barcode
- `mpn` - Manufacturer part number
- `brand` / `manufacturer` - Brand name
- `price` - Price as text (e.g., "$350.00")
- `price_numeric` - Price as number (e.g., 350.00)
- `in_stock` - Boolean stock status
- `category` - Product category
- `description_short` - Brief description
- `description_full` - Complete product description
- `url` - Product page URL
- `image_1` through `image_9` - Individual image URLs
- `all_images` - Pipe-separated list of all images
- `specifications_json` - JSON string of specifications

### JSON Format (`als_taping_tools_catalog.json`)
Nested JSON array with complete product objects including:
```json
{
  "name": "10\" Easy Clean Standard Axle Flat Finishing Box",
  "sku": "DM-10DMFF",
  "upc": "716894769724",
  "brand": "Drywall Master Tools",
  "price": "$350.00",
  "price_numeric": 350.0,
  "in_stock": true,
  "description_full": "Professional-Grade Design – Perfect for...",
  "specifications": {
    "Parts Url": "https://...",
    "Stand": "No"
  },
  "images": [
    "https://cdn11.bigcommerce.com/s-dbb3r9a7se/images/stencil/1280x1280/products/1968/6221/10__53717.1757516200.jpg",
    "https://cdn11.bigcommerce.com/s-dbb3r9a7se/images/stencil/1280x1280/products/1968/6224/10_2__48954.1757516200.jpg",
    ...
  ],
  "url": "https://www.alstapingtools.com/10-easy-clean-standard-axle-flat-finishing-box/"
}
```

## Features

### Comprehensive Data Extraction
- **All Product Pages**: Automatically discovers and scrapes every product
- **All Listing Pages**: Handles pagination automatically
- **High-Resolution Images**: Extracts 1280x1280px images (not thumbnails)
- **Complete Descriptions**: Both short and full product descriptions
- **Structured Specifications**: Parses specification tables

### Robust & Reliable
- **Progress Tracking**: Resume from interruption
- **Error Handling**: Continues on failures
- **Rate Limiting**: Respects server with delays
- **Retry Logic**: Automatically retries failed requests

### Flexible Output
- **CSV**: Easy to import into Excel, Google Sheets, databases
- **JSON**: Perfect for APIs, web applications, data processing
- **Multiple Image Columns**: Individual columns + combined list

## Expected Results

Based on the website structure:
- **Total Products**: ~1,000-2,000 products (estimated)
- **Images Per Product**: Average 3-9 images
- **Runtime**: 1-3 hours (depending on product count)
- **File Sizes**:
  - CSV: ~2-5 MB
  - JSON: ~3-8 MB

## Configuration

Edit the script to customize:

```python
# Delay between requests (seconds)
DELAY = 2.0  # Increase if getting rate limited

# Output paths
OUTPUT_CSV = "/path/to/output.csv"
OUTPUT_JSON = "/path/to/output.json"

# Starting URL (default scrapes all products)
START_URL = "https://www.alstapingtools.com/shop-by-product/?mode=4&sort=alphaasc&limit=100"
```

## Scraping Strategy

### 1. Discovery Phase
```
https://www.alstapingtools.com/shop-by-product/?limit=100
  ↓
Extract all product URLs from listing
  ↓
Follow pagination to next pages
  ↓
Compile complete list of product URLs
```

### 2. Extraction Phase
```
For each product URL:
  ↓
Visit product page
  ↓
Extract:
  - Basic info (name, SKU, price)
  - Descriptions (short & full)
  - Images (all available)
  - Specifications (from tables)
  - Metadata (brand, category, stock)
  ↓
Save to results
```

### 3. Output Phase
```
All products collected
  ↓
Convert to CSV format
  ↓
Convert to JSON format
  ↓
Save both files
```

## Image Extraction Details

The scraper extracts ALL product images in high resolution:

1. **Primary Product Image**: Main display image
2. **Gallery Images**: All gallery/carousel images
3. **Thumbnail Images**: Converted to high-res versions
4. **Resolution**: 1280x1280px (highest available)
5. **Format**: Direct CDN URLs for downloading

Example images extracted per product:
- Product in use
- Product from different angles
- Product components/parts
- Product packaging
- Technical diagrams
- Size comparisons

## Data Quality

### Product Names
- Clean, formatted names
- No HTML artifacts
- Proper capitalization

### Descriptions
- Full HTML-free text
- Bullet points preserved
- Technical specifications included

### Images
- High-resolution (1280x1280)
- Direct CDN links
- All available angles
- Verified image URLs

### Prices
- Text format (e.g., "$350.00")
- Numeric format (e.g., 350.0)
- Handles sales prices
- Captures "Out of Stock" items

## Resume Capability

If the scraper is interrupted:
1. Progress is automatically saved after each product
2. Simply run the script again
3. It will skip already-scraped products
4. Continues from where it left off

Progress file: `als_scraper_progress.json`

## Performance

**Optimization Tips:**
- Adjust `DELAY` for faster/slower scraping
- Run during off-peak hours
- Use stable internet connection
- Don't run multiple instances simultaneously

**Estimated Times:**
- 1000 products: ~1 hour
- 2000 products: ~2 hours
- 100 products/hour average

## Troubleshooting

### No Products Found
- Check if website structure changed
- Verify START_URL is correct
- Check internet connection

### Missing Images
- Some products may have no images
- Verify CDN URLs are accessible
- Check image extraction logic

### Price Extraction Fails
- Prices may require login (if so, noted in output)
- Check price element selectors
- Some items may not have prices

### Scraper Stops
- Check progress file
- Review last product scraped
- Run again to resume

## Use Cases

### E-commerce
- Import products into your store
- Price monitoring
- Competitor analysis
- Inventory management

### Data Analysis
- Market research
- Price trends
- Product categorization
- Brand analysis

### Content Management
- Product database
- Image library
- Description repository
- Specification lookup

## Legal & Ethical

- For educational and research purposes
- Includes rate limiting and delays
- Respects robots.txt
- Does not overload server
- Consider contacting ALS for official data access

## Advanced Usage

### Scrape Specific Category
```python
START_URL = "https://www.alstapingtools.com/shop-by-product/automatic-taping-tools/?limit=100"
```

### Scrape Specific Brand
```python
START_URL = "https://www.alstapingtools.com/shop-by-manufacturer/tapetech/?limit=100"
```

### Export to Database
```python
import sqlite3
import json

# Load JSON
with open('als_taping_tools_catalog.json') as f:
    products = json.load(f)

# Insert into database
conn = sqlite3.connect('products.db')
c = conn.cursor()

for product in products:
    c.execute('''INSERT INTO products VALUES (?, ?, ?, ?, ...)''',
              (product['name'], product['sku'], ...))

conn.commit()
```

## Support

For issues:
1. Check progress file for last state
2. Review console output for errors
3. Verify website accessibility
4. Try reducing DELAY if timeout errors

## Version

- **Version**: 1.0
- **Created**: January 2026
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Python**: 3.6+

---

## Sample Output Preview

```csv
name,sku,price,brand,image_1,image_2
"10"" Easy Clean Flat Box",DM-10DMFF,$350.00,Drywall Master Tools,https://cdn11...,https://cdn11...
"12"" Easy Clean Flat Box",DM-12DMFF,$360.00,Drywall Master Tools,https://cdn11...,https://cdn11...
```

Ready to create your complete ALS Taping Tools product catalog!
