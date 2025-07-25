import pandas as pd
import os
from urllib.parse import urlparse

# Get current working directory and define the CSV file path
cwd = os.getcwd()
file_path = os.path.join(cwd, 'artifact/result/100_test_app_link.csv')

# Read the full CSV file
df = pd.read_csv(file_path)

# Extract domain function with cleaning rules
def extract_domain(url):
    if not isinstance(url, str):
        return ""
    url = url.strip()
    if url.lower() in ["skip", "not found", ""]:
        return ""
    if not url.startswith("http") and not url.startswith("www."):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

# Apply domain extraction
df['domain'] = df['delete_account_url'].apply(extract_domain)

# Save the updated DataFrame back to the same CSV file
df.to_csv(file_path, index=False)
print("Domain extraction completed and saved to CSV.")
