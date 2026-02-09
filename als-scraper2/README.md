# AlsTapingTools.com Comprehensive Product Scraper

A professional-grade web scraping solution that extracts **ALL products** from AlsTapingTools.com including:
- Product names
- SKU numbers
- Prices
- Descriptions
- Product images (URLs and downloads)
- Complete metadata

## 📋 Features

### Core Capabilities
✅ **Complete Website Crawling** - Discovers and scrapes every page on the site
✅ **Product Detection** - Intelligently identifies product pages
✅ **Comprehensive Data Extraction**:
   - Product names and titles
   - SKU/model numbers
   - Prices (multiple format support)
   - Full descriptions
   - All product images
✅ **Image Management**:
   - Extracts all image URLs
   - Downloads images locally
   - Organizes by product
✅ **Multiple Export Formats**:
   - CSV (Excel-compatible)
   - JSON (developer-friendly)
   - Text report (summary)
✅ **Respectful Scraping**:
   - Configurable delays
   - Retry logic
   - Error handling
✅ **Web Interface**:
   - Real-time progress tracking
   - Live status updates
   - Visual data preview

## 🚀 Quick Start

### Option 1: Command Line (Standalone Python Script)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python als_scraper.py
```

**Output Files:**
- `alstapingtools_products.csv` - All products in CSV format
- `alstapingtools_products.json` - All products in JSON format
- `product_images/` - Downloaded product images
- `scrape_report.txt` - Summary report
- `scraper.log` - Detailed execution log

### Option 2: Web Application (With Visual Interface)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

Then open your browser to: **http://localhost:5000**

The web interface provides:
- Visual configuration
- Real-time progress monitoring
- Live product preview
- Download buttons for all data formats

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- Internet connection

### Step-by-Step Setup

1. **Clone or download this project**
```bash
# If using git
git clone <repository-url>
cd als-scraper

# Or simply download the files to a folder
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the scraper**
```bash
# Command line version:
python als_scraper.py

# Web application version:
python app.py
```

## 🎯 Usage Examples

### Basic Scraping (Python Script)

```python
from als_scraper import AlsTapingToolsScraper

# Initialize scraper
scraper = AlsTapingToolsScraper()

# Scrape all products
products = scraper.scrape_all_products()

# Save results
scraper.save_to_csv('products.csv')
scraper.save_to_json('products.json')

# Print summary
scraper.generate_report()
```

### Custom Configuration

```python
# Custom base URL and settings
scraper = AlsTapingToolsScraper(base_url="http://alstapingtools.com")
scraper.delay = 2.0  # 2 second delay between requests
scraper.timeout = 45  # 45 second timeout

# Scrape
products = scraper.scrape_all_products()
```

### Accessing Product Data

```python
for product in scraper.products:
    print(f"Name: {product['product_name']}")
    print(f"SKU: {product['sku']}")
    print(f"Price: {product['price']}")
    print(f"Description: {product['description']}")
    print(f"Images: {product['image_count']}")
    print(f"URL: {product['url']}")
    print("-" * 50)
```

## 📊 Output Data Format

### CSV Format
```csv
product_name,sku,price,description,url,image_urls,local_images,image_count,scraped_at
"TapeTech 7in Flat Box","SKU-1001","$159.99","Professional drywall finishing tool...","http://...","img1.jpg|img2.jpg","product_images/...","2","2024-02-08T10:30:00"
```

### JSON Format
```json
{
  "product_name": "TapeTech 7in Flat Box",
  "sku": "SKU-1001",
  "price": "$159.99",
  "description": "Professional drywall finishing tool...",
  "url": "http://alstapingtools.com/product/123",
  "image_urls": "http://example.com/img1.jpg|http://example.com/img2.jpg",
  "local_images": "product_images/TapeTech_0.jpg|product_images/TapeTech_1.jpg",
  "image_count": 2,
  "scraped_at": "2024-02-08T10:30:00"
}
```

## 🔧 Configuration Options

### Scraper Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | "http://alstapingtools.com" | Website to scrape |
| `delay` | 1.5 | Seconds between requests |
| `timeout` | 30 | Request timeout in seconds |
| `image_folder` | "product_images" | Where to save images |

### Modifying Settings in Python

```python
scraper = AlsTapingToolsScraper()
scraper.delay = 2.0  # Slower, more respectful
scraper.timeout = 60  # Longer timeout for slow connections
```

### Modifying Settings in Web App

Use the configuration panel in the web interface:
- URL input field
- Delay slider
- Checkboxes for features

## 📁 Project Structure

```
als-scraper/
├── als_scraper.py          # Main scraper script
├── app.py                  # Flask web application
├── scraper_app.html        # Web interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── product_images/        # Downloaded images (created automatically)
├── alstapingtools_products.csv   # Output file
├── alstapingtools_products.json  # Output file
├── scrape_report.txt      # Summary report
└── scraper.log           # Execution log
```

## 🛡️ Features & Capabilities

### Intelligent Product Detection
The scraper uses multiple strategies to identify product pages:
- Class name patterns (`product`, `item`, etc.)
- Schema.org markup detection
- URL pattern matching
- Meta tag analysis

### Robust Data Extraction

**Product Names:** Extracted from:
- H1 tags
- Title tags
- Product-specific CSS classes
- Schema.org markup

**Prices:** Extracted from:
- Price-specific classes/IDs
- Schema.org price fields
- Meta tags
- Pattern matching (e.g., "$99.99")

**SKUs:** Extracted from:
- SKU-specific classes/IDs
- Schema.org SKU fields
- Data attributes
- Text pattern matching

**Descriptions:** Extracted from:
- Description containers
- Meta descriptions
- Product detail sections

**Images:** Extracted from:
- Product image galleries
- Main product images
- Zoom images
- Schema.org images
- Open Graph images

### Error Handling
- Automatic retry on failed requests
- Timeout handling
- Network error recovery
- Malformed HTML handling
- Graceful degradation

## 📈 Performance

- **Average speed:** 10-30 products per minute (depends on delay setting)
- **Memory efficient:** Streams data to files
- **Scalable:** Can handle thousands of products
- **Respectful:** Built-in delays to avoid server overload

## 🔍 Troubleshooting

### Common Issues

**1. Network Connection Errors**
```
Error: Failed to resolve 'alstapingtools.com'
```
**Solution:** Check your internet connection and verify the URL is correct.

**2. Timeout Errors**
```
Error: Request timeout after 30 seconds
```
**Solution:** Increase the timeout value:
```python
scraper.timeout = 60
```

**3. No Products Found**
```
Scraping complete! Total products found: 0
```
**Solution:** 
- Verify the website structure hasn't changed
- Check the logs for specific errors
- Try increasing the delay value

**4. Permission Errors (Images)**
```
Error: Permission denied writing to product_images/
```
**Solution:** Ensure you have write permissions in the directory.

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Legal & Ethical Considerations

### Important Notes:
1. **Respect robots.txt** - Check the website's robots.txt file
2. **Terms of Service** - Review the website's terms before scraping
3. **Rate Limiting** - Use appropriate delays (default: 1.5s)
4. **Personal Use** - This tool is for personal/educational use
5. **Copyright** - Product data and images may be copyrighted

### Best Practices:
- ✅ Use reasonable delay values (1-3 seconds)
- ✅ Scrape during off-peak hours
- ✅ Cache results to avoid re-scraping
- ✅ Respect the website's resources
- ❌ Don't overload servers with requests
- ❌ Don't use scraped data commercially without permission

## 🤝 Contributing

Feel free to improve this scraper:
- Add new data extraction methods
- Improve error handling
- Enhance the web interface
- Add new export formats

## 📄 License

This project is provided as-is for educational purposes.

## 🆘 Support

If you encounter issues:
1. Check the `scraper.log` file for detailed errors
2. Review the troubleshooting section above
3. Ensure all dependencies are installed correctly
4. Verify the website is accessible

## 🔄 Updates & Maintenance

### Website Changes
If the website structure changes, you may need to update:
- CSS selectors in extraction methods
- URL patterns for product detection
- Image URL extraction logic

### Keeping Up to Date
```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt
```

## ✨ Advanced Usage

### Custom Extraction Functions

Add your own extraction logic:
```python
class CustomScraper(AlsTapingToolsScraper):
    def extract_custom_field(self, soup):
        # Your custom extraction logic
        element = soup.find('div', class_='custom-field')
        return element.get_text() if element else 'N/A'
```

### Filtering Products

```python
# Only products with prices
products_with_prices = [p for p in scraper.products if p['price'] != 'N/A']

# Only products with images
products_with_images = [p for p in scraper.products if p['image_count'] > 0]

# Products in specific price range
expensive_products = [p for p in scraper.products 
                      if p['price'] != 'N/A' and float(p['price'].replace('$','')) > 100]
```

### Exporting to Excel with Formatting

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame(scraper.products)

# Export to Excel with formatting
with pd.ExcelWriter('products.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Products', index=False)
```

## 🎓 Learning Resources

- **BeautifulSoup Documentation:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Requests Documentation:** https://docs.python-requests.org/
- **Web Scraping Ethics:** https://www.scrapehero.com/web-scraping-legal/

---

**Happy Scraping! 🚀**

*Remember to scrape responsibly and ethically!*
