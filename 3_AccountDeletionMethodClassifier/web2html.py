import os
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



def fetch_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 ...")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        print(f"[Selenium] Failed: {url} | Error: {e}")
        return None

# This function saves the HTML content of a URL to a file if it does not already exist.
def save_url_as_html_if_needed(url, output_path, filename):
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, filename)

    if os.path.exists(file_path):
        print(f"[Skip] Already exists: {file_path}")
        return

    # add http:// or https:// if not present
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    html = fetch_with_selenium(url)

    if html:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[Saved] {file_path}")
    else:
        print(f"[Error] Failed to save: {url}")

cwd = os.getcwd()
input_csv = cwd + '/artifact/result/100_test_app_link.csv'

html_output_dir = cwd + '/artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/html_policies'

# make sure the output directory exists
if not os.path.exists(html_output_dir):
    os.makedirs(html_output_dir)

df = pd.read_csv(input_csv)

for idx, row in df.iterrows():
    url = str(row.get("delete_account_url", "")).strip().lower()
    if not url or url == "not found" or url == "nan" or url == "manual" or url == "skipping this app":
        continue  
    pkg_name = str(row.get("pkg_name", f"app_{idx}")).strip()
    filename = pkg_name + ".html"
    save_url_as_html_if_needed(url, html_output_dir, filename)
