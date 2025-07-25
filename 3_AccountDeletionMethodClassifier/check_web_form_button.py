import os
import pandas as pd
from bs4 import BeautifulSoup

# Keywords related to deletion actions (all lowercase)
delete_verbs = {
    "delete", "deletion", "remove", "removal", "close", "terminate", "termination",
    "cancel", "cancellation", "erase", "erasure", "withdraw", "unregister",
    "unsubscribe", "deregister", "stop", "end", "cease", "discontinue", "clear"
}

# ==== Detect if HTML contains user input forms ====
def detect_user_input_forms_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = soup.find_all('form')
    return len(forms) > 0

# ==== Detect if HTML contains delete-related buttons ====
def detect_delete_button_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    buttons = soup.find_all(['button', 'a', 'input'])  # Tags that can act as buttons
    for btn in buttons:
        text = (btn.get_text() or '') + ' ' + (btn.get('value') or '')  # Combine visible text and input value
        if any(verb in text.lower() for verb in delete_verbs):
            return True
    return False

# ==== Path Setup ====
cwd = os.getcwd()
input_path = os.path.join(cwd, 'artifact/result/100_test_app_link.csv')
html_dir = os.path.join(cwd, 'artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/html_policies')

# ==== Load Data and Process Each HTML File ====
df = pd.read_csv(input_path)
df['has_user_input_form'] = ""
df['has_delete_button'] = ""

for idx, row in df.iterrows():
    pkg_name = row.get('pkg_name')
    html_file = os.path.join(html_dir, f"{pkg_name}.html")

    if os.path.exists(html_file):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            has_form = detect_user_input_forms_from_html(html_content)
            has_delete = detect_delete_button_from_html(html_content)
        except Exception as e:
            print(f"[Error] Reading HTML for {pkg_name}: {e}")
            has_form, has_delete = "Error", "Error"
    else:
        print(f"[✗] No HTML file for {pkg_name}")
        has_form, has_delete = "No file", "No file"

    # Update detection results in the DataFrame
    df.at[idx, 'has_user_input_form'] = "Yes" if has_form is True else ("No" if has_form is False else has_form)
    df.at[idx, 'has_delete_button'] = "Yes" if has_delete is True else ("No" if has_delete is False else has_delete)

# ==== Save Updated Results ====
df.to_csv(input_path, index=False)
print(f"[✔] Updated CSV with form and button detection saved to: {input_path}")
