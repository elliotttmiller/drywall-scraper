# TSW Fast Product Scraper

Complete web scraping solution for extracting all products and specifications from tswfast.com

## Overview

This scraper extracts product data from the "Shop By Brand" section of TSW Fast, a tool and supply distributor. It can scrape:
- All brands (300+)
- All products per brand
- Product names, part numbers, images
- Product URLs for further data collection
- Optional: Detailed specifications by visiting each product page

## Files Included

1. **tswfast_complete_scraper.py** - Main scraper (recommended)
   - Scrapes all brands and products
   - Saves incrementally to CSV
   - Handles pagination
   - Progress tracking and resume capability
   - Rate limiting built-in

2. **product_detail_extractor.py** - Detail extraction module
   - Extracts specifications from individual product pages
   - Can be integrated with main scraper
   - Handles various HTML structures

3. **tswfast_scraper_demo.py** - Demo/example code
   - Shows data structure
   - Sample output format

## Quick Start

### Basic Scrape (Fast - Recommended First Run)
```bash
python3 tswfast_complete_scraper.py
```

This will:
- Scrape all brands and products
- Extract: brand, name, part number, URL, image
- Save to: `/mnt/user-data/outputs/tswfast_all_products.csv`
- Takes approximately: 30-60 minutes for all brands

### Detailed Scrape (Slow - For Specific Brands)
Edit `tswfast_complete_scraper.py` and set:
```python
GET_DETAILED_SPECS = True
```

This will visit each product page for complete specifications but takes much longer.

## Output Format

### CSV Columns:
| Column | Description | Example |
|--------|-------------|---------|
| brand | Brand/manufacturer name | 3M |
| product_name | Full product name | Angled Sanding Sponge - Fine Grit |
| part_number | SKU/Part number | THR07053 |
| url | Full product URL | https://www.tswfast.com/product/THR07053 |
| image_url | Product image URL | https://s3.amazonaws.com/.../THR07053_Medium.jpg |
| short_description | Brief description | (if available) |
| category | Product category | (if available) |
| specifications | JSON of detailed specs | (if detailed mode enabled) |

## Features

### ✅ Robust Error Handling
- Retries failed requests
- Continues on errors
- Saves progress automatically

### ✅ Progress Tracking
- Saves progress after each brand
- Resume from interruption
- Progress file: `scraper_progress.json`

### ✅ Rate Limiting
- Built-in delays between requests
- Respectful to server
- Configurable timing

### ✅ Incremental Saving
- Writes to CSV after each brand
- No data loss on interruption
- Can view partial results

## Website Structure

### Brand Pages
- Main URL: `https://www.tswfast.com/category/tools_shop_by_brand`
- Brand pattern: `/category/brand_[BrandName]`
- ~300+ brands total

### Product Listings
- Each brand page shows products in grid
- Some brands have 1-100+ products
- Product URLs: `/product/[PartNumber]`

### Known Limitations
1. **Prices require login** - Not extracted
2. **Some specs require product page visit** - Use detailed mode
3. **Rate limiting** - Full scrape takes time
4. **Network required** - Must have internet access

## Customization

### Adjust Rate Limiting
```python
DELAY_BETWEEN_REQUESTS = 1.5  # Increase for more respectful scraping
```

### Change Output Location
```python
OUTPUT_FILE = "/path/to/your/output.csv"
```

### Resume From Specific Brand
Edit `scraper_progress.json`:
```json
{
  "last_brand_index": 50,
  "brands_completed": [...]
}
```

## Troubleshooting

### Network Errors
- Check internet connection
- Website might be temporarily down
- Try increasing delay between requests

### Missing Data
- Some fields may be empty (normal)
- Prices always show "Login Required"
- Use detailed mode for more specs

### Script Interrupted
- Don't worry! Progress is saved
- Just run again - it will resume
- Check `scraper_progress.json` for status

## Example Output

```csv
brand,product_name,part_number,url,image_url
3M,Angled Sanding Sponge - Fine Grit,THR07053,https://www.tswfast.com/product/THR07053,https://s3.amazonaws.com/.../THR07053_Medium.jpg
3M,ScotchBlue Original Painter's Tape,THR209036ACP,https://www.tswfast.com/product/...,https://...
DeWalt,20V MAX Drill Driver,DWD120K,https://www.tswfast.com/product/...,https://...
```

## Performance

- **Quick mode**: ~300 brands in 30-60 min (~10,000-20,000 products)
- **Detailed mode**: Much slower, only recommended for targeted scraping
- **Memory usage**: Minimal (writes incrementally)
- **Disk space**: ~5-10 MB for full dataset

## Legal & Ethical Considerations

- This scraper includes rate limiting and respectful delays
- For educational and research purposes
- Review website's Terms of Service and robots.txt
- Consider reaching out to TSW Fast for official data access

## Advanced Usage

### Scrape Specific Brands Only
Modify the main loop:
```python
target_brands = ['3M', 'DeWalt', 'Makita']
for brand in brands:
    if brand['name'] in target_brands:
        # scrape this brand
```

### Export to Different Format
The CSV can be easily converted:
```python
import pandas as pd
df = pd.read_csv('tswfast_all_products.csv')
df.to_json('products.json', orient='records')
df.to_excel('products.xlsx', index=False)
```

## Support

For issues or questions:
1. Check the progress file: `scraper_progress.json`
2. Review the output CSV for partial data
3. Adjust rate limiting if getting errors
4. Try detailed mode for specific products

## Version History

- v1.0 - Initial complete scraper with progress tracking
- Includes comprehensive error handling and documentation

---

**Note**: Pricing information requires authentication and is not included in the scrape.
