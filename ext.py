import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

# ========== SETTINGS ==========
URL = "https://makerselectronics.com/product/nvidia-jetson-agx-xavier-64gb-with-forcer-carrier-board-rev1-1/"   # 🔴 حط موقع Pyresearch
OUTPUT_DIR = "m3"
# ==============================

os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(f"{OUTPUT_DIR}/css", exist_ok=True)
# os.makedirs(f"{OUTPUT_DIR}/images", exist_ok=True)
# os.makedirs(f"{OUTPUT_DIR}/fonts", exist_ok=True)

# ========= 1️⃣ Selenium =========
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)
time.sleep(5)

html = driver.page_source
driver.quit()

# ========= 2️⃣ Parse HTML =========
soup = BeautifulSoup(html, "html.parser")

# ========= 3️⃣ CSS =========
all_css = ""

for link in soup.find_all("link", rel="stylesheet"):
    href = link.get("href")
    if not href:
        continue

    css_url = urljoin(URL, href)

    # 🚫 تجاهل blob / data
    # if css_url.startswith("blob:") or css_url.startswith("data:"):
    #     print(f"⚠ Skipped CSS: {css_url}")
    #     continue

    # try:
    #     css_resp = requests.get(css_url, timeout=10)
    #     css_resp.raise_for_status()
    #     all_css += f"\n/* {css_url} */\n{css_resp.text}"
    #     link["href"] = "css/styles.css"
    #     print(f"✔ CSS loaded: {css_url}")
    # except Exception as e:
    #     print(f"❌ CSS failed: {css_url} -> {e}")

for style in soup.find_all("style"):
    all_css += "\n/* inline style */\n" + style.text
    style.decompose()

# ========= 4️⃣ Download files =========
def download_file(url, folder):
    if url.startswith("blob:") or url.startswith("data:"):
        return None

    name = os.path.basename(urlparse(url).path)
    if not name:
        return None

    path = f"{OUTPUT_DIR}/{folder}/{name}"
    if not os.path.exists(path):
        try:
            r = requests.get(url, timeout=10)
            with open(path, "wb") as f:
                f.write(r.content)
        except:
            return None

    return f"{folder}/{name}"


# for img in soup.find_all("img"):
#     src = img.get("src")
#     if src:
#         full = urljoin(URL, src)
#         local = download_file(full, "images")
#         if local:
#             img["src"] = local

# def replace_assets(css, folder):
#     urls = re.findall(r'url\(["\']?(.*?)["\']?\)', css)
#     for u in urls:
#         if u.startswith("data:"):
#             continue
#         full = urljoin(URL, u)
#         local = download_file(full, folder)
#         if local:
#             css = css.replace(u, local)
#     return css

# all_css = replace_assets(all_css, "images")
# all_css = replace_assets(all_css, "fonts")

# with open(f"{OUTPUT_DIR}/css/styles.css", "w", encoding="utf-8") as f:
#     f.write(all_css)

with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Conversion finished!")
