import os
import pandas as pd
import csv
from openai import OpenAI

# === Path Setup ===
cwd = os.getcwd()
input_path = os.path.join(cwd, 'artifact/result/100_test_app_link.csv')
html_dir = os.path.join(cwd, 'artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/html_policies')
txt_dir = os.path.join(cwd, 'artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/plaintext_policies')

# === OpenAI API Setup ===
client = OpenAI(api_key="")

def chatgpt_classify(content):
    prompt = (
        "Prompt: You are tasked with reviewing the content and classifying the method(s) it describes for account deletion method (ADM). "
        "There are five possible categories: "
        "1. Missing ADM: The content does not include any content related to ADM. "
        "2. In-app path ADM: The content describes the specific steps or navigation paths users can follow within an app (on Android, iOS, or mobile platforms) to delete their account. "
        "3. Web-based ADM: The content provides a direct URL or interface where users can input their information and delete their account online. "
        "4. Alternative ADM: The content provides alternative methods such as email, telephone and so on. "
        "Tasks: "
        "1. Review the following content. "
        "2. Determine which of the above categories apply (it can be one or more). "
        "3. Output the classification as follows: [Missing], [Alternative-xxx], [In-app path], [Web-based], [Input content error].\n\n"
        f"Content:\n{content}"
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert of Google Data Safety Section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ Error on attempt {attempt+1}: {e}")
    return "Error: Max retries exceeded"

# === Load Input CSV ===
df = pd.read_csv(input_path)
df["GPT_Classification"] = ""  # Init new columns
df["has_text"] = ""

# === Process Each Row ===
for idx, row in df.iterrows():
    pkg_name = row["pkg_name"]
    txt_path = os.path.join(txt_dir, f"{pkg_name}.txt")

    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
                classification = chatgpt_classify(content)
                df.at[idx, "GPT_Classification"] = classification
                df.at[idx, "has_text"] = "Yes"
                print(f"[✓] {pkg_name} → {classification}")
        except Exception as e:
            print(f"[Error] Reading {pkg_name}: {e}")
            df.at[idx, "GPT_Classification"] = f"Error reading txt: {e}"
            df.at[idx, "has_text"] = "Yes"
    else:
        df.at[idx, "has_text"] = "No"
        print(f"[✗] {pkg_name} → No txt found")

# === Save Updated CSV ===
df.to_csv(input_path, index=False)
print(f"[✔] Results saved to: {input_path}")
