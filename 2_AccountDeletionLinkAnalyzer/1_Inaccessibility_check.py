import pandas as pd
import requests
import random
import csv
import os

cwd = os.getcwd()
file_path = cwd + '/artifact/result/100_test_app_link.csv'

# List of User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
]

# Define a function to check URL availability
def check_url(url):
    if not url or url.strip().lower() == "not found":  # Check if URL is empty or 'not found'
        return "skip"

    url = url.strip()  # Strip whitespace

    # Ensure proper URL scheme
    if not url.startswith(("http://", "https://")):
        url_https = f"https://{url}"
        url_http = f"http://{url}"
    else:
        url_https = url_http = url

    # Try HTTPS first
    try:
        response = requests.get(url_https, timeout=10, headers={"User-Agent": random.choice(user_agents)})
        if response.status_code == 200:
            return "accessible"
        return f"no: HTTP {response.status_code}"
    except requests.RequestException as e:
        error_https = str(e)

    # Try HTTP if HTTPS fails
    try:
        response = requests.get(url_http, timeout=10, headers={"User-Agent": random.choice(user_agents)})
        if response.status_code == 200:
            return "accessible"
        return f"no: HTTP {response.status_code}"
    except requests.RequestException as e:
        error_http = str(e)

    # If both HTTPS and HTTP fail, return error messages
    return f"no: {error_https if 'error_https' in locals() else ''} | {error_http if 'error_http' in locals() else ''}".strip(" | ")

# Read and write rows one by one
temp_file = file_path + ".temp"  # Create a temporary file

with open(file_path, mode='r', encoding='utf-8', newline='') as infile, open(temp_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    if "delete_account_url_available" not in fieldnames:
        fieldnames.append("delete_account_url_available")  # Add new column if missing
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        url = row.get("delete_account_url", "")  # Get the URL, default to empty string if None
        url = url.strip() if url else ""  # Strip if not None

        current_status = row.get("delete_account_url_available", "").strip() if row.get("delete_account_url_available") else ""

        # If status already exists, skip checking
        if current_status:
            print(f"Skipping {url}: already checked ({current_status})")
        else:
            result = check_url(url)
            print(f"Checked {url}: {result}")
            row["delete_account_url_available"] = result  # Record the result
        
        writer.writerow(row)  # Write row by row

# Replace original file with the updated file
os.replace(temp_file, file_path)

print(f"Check completed. Results have been updated to {file_path}")
