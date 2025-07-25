import os
import re
import spacy
import pandas as pd

# ---------- Path Setup ----------
cwd = os.getcwd()
input_csv = os.path.join(cwd, 'artifact/result/100_test_app_link.csv')
txt_dir = os.path.join(cwd, 'artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/plaintext_policies')

# ---------- Load Data ----------
df_apps = pd.read_csv(input_csv)
df_apps['Processed App Name'] = df_apps['app_name'].str.split(':').str[0].str.strip().str.lower()
app_names = df_apps['Processed App Name'].tolist()

# ---------- Load spaCy NLP Model ----------
nlp = spacy.load("en_core_web_sm")

# ---------- Detection Function ----------
def detect_in_app_path(text):
    phrase_patterns = [
        r"open\s+\w+\s+app",
        r"opening\s+\w+\s+app",
        r"tap\s+\w+\s+profile",
        r"tapping\s+\w+\s+profile",
        r"tap\s+\w+\s+settings",
        r"tapping\s+\w+\s+settings"
    ]

    for pattern in phrase_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    doc = nlp(text)
    for token in doc:
        if token.lemma_ in ["open", "opening"] and token.pos_ == "VERB":
            for child in token.children:
                if child.dep_ == "dobj":
                    subtree = " ".join(t.text.lower() for t in child.subtree)
                    if any(app_name in subtree for app_name in app_names):
                        return True

        elif token.lemma_ in ["tap", "tapping"] and token.pos_ == "VERB":
            if any(child.dep_ == "dobj" and child.text.lower() in ["settings", "profile", "avatar"]
                   for child in token.children):
                return True

        elif token.lemma_ in ["delete", "deleting"] and token.pos_ == "VERB":
            has_account = any(c.dep_ == "dobj" and "account" in c.text.lower() for c in token.children)
            has_in_app = any(
                c.dep_ in ["prep", "pobj", "advmod"] and any(
                    p in c.text.lower() for p in ["application", "app", "in-app", "within the app", "via the app"]
                ) for c in token.children
            )
            if has_account and has_in_app:
                return True

    return False

# ---------- Process Text Files and Map Results ----------
in_app_results = {}

for filename in os.listdir(txt_dir):
    if not filename.endswith(".txt"):
        continue

    pkg_name = filename.replace(".txt", "")
    file_path = os.path.join(txt_dir, filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            in_app_results[pkg_name] = "Yes" if detect_in_app_path(text) else "No"
    except Exception as e:
        print(f"[Error] Could not read {file_path}: {e}")
        in_app_results[pkg_name] = "Error"

# ---------- Update and Save ----------
df_apps["StepbyStep"] = df_apps["pkg_name"].map(in_app_results).fillna("Unknown")
df_apps.drop(columns=["Processed App Name"], inplace=True)

df_apps.to_csv(input_csv, index=False)
print(f"[Done] 'StepbyStep' column added to: {input_csv}")
