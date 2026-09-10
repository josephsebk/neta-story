#!/usr/bin/env python3
"""Export the Overheard at GFF carousel as 1080x1350 PNGs using Selenium."""

import os, time, zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SLIDE_W, SLIDE_H = 1080, 1350
TOTAL_SLIDES = 9
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(OUT_DIR, "carousel_out")
ZIP_PATH = os.path.join(OUT_DIR, "gff_carousel.zip")
HTML_PATH = os.path.join(OUT_DIR, "carousel.html")

os.makedirs(PNG_DIR, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1400,1600")
opts.add_argument("--force-device-scale-factor=1")
opts.add_argument("--hide-scrollbars")

driver = webdriver.Chrome(options=opts)
driver.get(f"file://{HTML_PATH}")

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".slide.active"))
)
# Playfair Display in particular needs a beat to settle before capture.
driver.execute_script("return document.fonts.ready")
time.sleep(2.5)

driver.execute_script("""
    document.querySelector('.controls').style.display = 'none';
    document.body.style.background = '#f5f0e8';
    document.querySelector('.viewport').style.padding = '0';
    document.querySelector('.viewport').style.minHeight = '0';
""")

pngs = []
for idx in range(TOTAL_SLIDES):
    driver.execute_script(f"""
        document.querySelectorAll('.slide').forEach(s => {{
            s.classList.remove('active');
            s.style.display = 'none';
        }});
        const s = document.querySelectorAll('.slide')[{idx}];
        s.classList.add('active');
        s.style.display = 'flex';
    """)
    time.sleep(0.7)
    slide = driver.find_elements(By.CSS_SELECTOR, ".slide")[idx]
    png_data = slide.screenshot_as_png
    fname = f"gff_slide_{idx+1:02d}.png"
    with open(os.path.join(PNG_DIR, fname), "wb") as f:
        f.write(png_data)
    pngs.append((fname, png_data))
    print(f"  Captured {fname}  ({len(png_data)//1024} KB)")

driver.quit()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname, data in pngs:
        zf.writestr(fname, data)

print(f"\nDone. {len(pngs)} slides written to:")
print(f"  PNGs:  {PNG_DIR}")
print(f"  ZIP:   {ZIP_PATH}  ({os.path.getsize(ZIP_PATH)//1024} KB)")
