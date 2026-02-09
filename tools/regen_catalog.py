import json
from pathlib import Path

BASE = Path(r"d:/AMD/projects/scraper")
JSONL = BASE / 'als_taping_tools_catalog.jsonl'
OUT_JSONL = BASE / 'als_taping_tools_catalog.jsonl.tmp'
OUT_JSON = BASE / 'als_taping_tools_catalog.json'
OUT_CSV = BASE / 'als_taping_tools_catalog.csv'

fieldnames = [
    'brand', 'name', 'description_full', 'sku', 'upc',
    'price', 'price_numeric', 'description_short',
    'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'image_9',
    'all_images'
]

if not JSONL.exists():
    print(f"Source JSONL not found: {JSONL}")
    raise SystemExit(1)

products = []
with JSONL.open('r', encoding='utf-8') as inf, OUT_JSONL.open('w', encoding='utf-8') as outf:
    for line in inf:
        line = line.strip()
        if not line:
            continue
        try:
            p = json.loads(line)
        except Exception as e:
            print('Skipping invalid JSON line:', e)
            continue
        # remove unwanted keys
        for k in ('url', 'mpn', 'in_stock', 'specifications', 'manufacturer', 'category'):
            p.pop(k, None)
        # normalize images
        imgs = p.get('images') or []
        p['images'] = imgs
        # write cleaned jsonl
        outf.write(json.dumps(p, ensure_ascii=False) + '\n')
        products.append(p)

# overwrite original jsonl
OUT_JSONL.replace(JSONL)

# write final pretty json
with OUT_JSON.open('w', encoding='utf-8') as fj:
    json.dump(products, fj, indent=2, ensure_ascii=False)

# write CSV
import csv
with OUT_CSV.open('w', newline='', encoding='utf-8') as cf:
    writer = csv.DictWriter(cf, fieldnames=fieldnames)
    writer.writeheader()
    for p in products:
        row = {k: '' for k in fieldnames}
        row['brand'] = p.get('brand', '')
        row['name'] = p.get('name', '')
        row['description_full'] = p.get('description_full', '')
        row['sku'] = p.get('sku', '')
        row['upc'] = p.get('upc', '')
        row['price'] = p.get('price', '')
        row['price_numeric'] = p.get('price_numeric', '')
        row['description_short'] = p.get('description_short', '')
        imgs = p.get('images', [])
        for i in range(9):
            key = f'image_{i+1}'
            row[key] = imgs[i] if i < len(imgs) else ''
        row['all_images'] = '|'.join(imgs)
        writer.writerow(row)

print('Regeneration complete:')
print(' -', OUT_CSV)
print(' -', OUT_JSON)
print(' -', JSONL)
