#!/usr/bin/env python3
"""Export neta_story carousel slides as 1080x1350 PNGs using Selenium."""

import os, time, zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SLIDE_W, SLIDE_H = 1080, 1350
TOTAL_SLIDES = 10
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(OUT_DIR, "carousel_out")
ZIP_PATH = os.path.join(OUT_DIR, "neta_story_carousel.zip")
HTML_PATH = os.path.join(OUT_DIR, "carousel.html")

os.makedirs(PNG_DIR, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1400,1600")
opts.add_argument("--force-device-scale-factor=1")
opts.add_argument("--hide-scrollbars")

driver = webdriver.Chrome(options=opts)
driver.get(f"file://{HTML_PATH}")

# Wait for fonts to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".slide.active"))
)
# Force-wait for web fonts (Playfair Display in particular)
driver.execute_script("return document.fonts.ready")
time.sleep(2)

# Hide controls bar and dark background so the slide sits clean on the page
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
    time.sleep(0.6)
    slide = driver.find_elements(By.CSS_SELECTOR, ".slide")[idx]
    png_data = slide.screenshot_as_png
    fname = f"neta_story_slide_{idx+1:02d}.png"
    with open(os.path.join(PNG_DIR, fname), "wb") as f:
        f.write(png_data)
    pngs.append((fname, png_data))
    print(f"  Captured {fname}")

driver.quit()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname, data in pngs:
        zf.writestr(fname, data)

print(f"\nDone. {len(pngs)} slides written to:")
print(f"  PNGs:  {PNG_DIR}")
print(f"  ZIP:   {ZIP_PATH}  ({os.path.getsize(ZIP_PATH)//1024} KB)")
