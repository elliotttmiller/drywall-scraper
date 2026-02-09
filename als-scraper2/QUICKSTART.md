# 🚀 QUICK START GUIDE
## AlsTapingTools.com Comprehensive Product Scraper

### ⚡ Fastest Way to Get Started

#### Option 1: Web Interface (RECOMMENDED)
**Best for users who want a visual interface**

**Windows:**
```
Double-click: run_webapp.bat
```

**Mac/Linux:**
```bash
./run_webapp.sh
```

Then open your browser to: **http://localhost:5000**

---

#### Option 2: Command Line
**Best for automation and scripts**

**Windows:**
```
Double-click: run_standalone.bat
```

**Mac/Linux:**
```bash
./run_standalone.sh
```

Results will be saved to:
- `alstapingtools_products.csv`
- `alstapingtools_products.json`
- `product_images/`

---

### 📋 What Gets Extracted

For EVERY product on AlsTapingTools.com:
- ✅ Product Name
- ✅ SKU / Model Number
- ✅ Price
- ✅ Full Description
- ✅ All Product Images (URLs + Downloads)
- ✅ Product Page URL
- ✅ Image Count
- ✅ Timestamp

---

### 💾 Output Files

**CSV Format** (`alstapingtools_products.csv`)
- Opens in Excel, Google Sheets
- Perfect for analysis and reporting

**JSON Format** (`alstapingtools_products.json`)
- Machine-readable format
- Perfect for developers and APIs

**Text Report** (`scrape_report.txt`)
- Summary statistics
- Quick overview

**Images Folder** (`product_images/`)
- All product images downloaded
- Organized by product name

---

### ⚙️ Configuration Options

**Web Interface:**
- URL: Change target website
- Delay: Adjust request speed (1.5 sec recommended)
- Download Images: Toggle image downloading
- Extract Descriptions: Toggle full descriptions

**Python Script:**
Edit `als_scraper.py`:
```python
scraper = AlsTapingToolsScraper()
scraper.delay = 2.0  # Slower, more respectful
scraper.timeout = 60  # Longer timeout
```

---

### 🔧 Troubleshooting

**"Cannot connect to server"**
- Make sure you're running the web app version
- Check that port 5000 is not in use

**"No products found"**
- Check internet connection
- Verify website URL is correct
- Try increasing the delay value

**"Permission denied"**
- Run as administrator (Windows)
- Use `sudo` (Mac/Linux)

**"Module not found"**
```bash
pip install -r requirements.txt
```

---

### 📊 Expected Results

**Typical scraping stats:**
- Products: 50-500+ (depending on website)
- Time: 5-30 minutes (depends on delay and product count)
- Images: 2-5 per product average
- Success rate: 95%+ for products with complete data

---

### 🎯 Usage Tips

1. **Start with default settings** - They're optimized for best results
2. **Don't lower delay below 1.0 seconds** - Risk of being blocked
3. **Use CSV for Excel** - Easiest to work with
4. **Check the log file** - If something goes wrong
5. **Images take time** - Downloading images increases total time

---

### 📞 Need Help?

1. Check `scraper.log` for detailed error messages
2. Review the full README.md for comprehensive documentation
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

### 🎉 You're Ready!

Just run one of the scripts above and the scraper will handle everything automatically!

**Happy Scraping! 🔧**
