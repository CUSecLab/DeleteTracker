import os
import csv
import spacy
import string
import pandas as pd

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 5000000

# Define keyword sets
delete_verbs = {
    "delete", "deletion", "remove", "removal", "close", "terminate", "termination",
    "cancel", "cancellation", "erase", "erasure", "withdraw", "unregister",
    "unsubscribe", "deregister", "stop", "end", "cease", "discontinue", "clear"
}

delete_nouns = {"account", "user", "profile", "subscription", "membership", "gameid", "userid"}
negation_words = {"not", "cannot", "never", "unable", "won’t", "doesn't", "can't", "no", "without", "refuse"}

# Paths
cwd = os.getcwd()
input_csv = os.path.join(cwd, 'artifact/result/100_test_app_link.csv')
txt_dir = os.path.join(cwd, 'artifact/3_AccountDeletionMethodClassifier/HtmlToPlaintext-master/ext/plaintext_policies')

# Load data
df = pd.read_csv(input_csv)
url_dict = dict(zip(df["pkg_name"], df["delete_account_url"].fillna("").astype(str)))
pkg_list = df["pkg_name"].tolist()

# Helper: check URL for deletion-related terms
def match_url_keywords(url, window=10):
    cleaned_url = url.replace("-", " ").replace("_", " ").replace("/", " ").replace(".", " ") \
                     .replace("~", " ").replace("#", " ").replace("$", " ").replace("%", " ") \
                     .replace("*", " ").replace(":", " ")
    doc = nlp(cleaned_url.lower())
    lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_space]

    for i, word in enumerate(lemmas):
        if word in delete_verbs:
            for j in range(i + 1, min(i + window, len(lemmas))):
                if lemmas[j] in delete_nouns:
                    return True
        if word in delete_nouns:
            for j in range(i + 1, min(i + window, len(lemmas))):
                if lemmas[j] in delete_verbs:
                    return True
    return False

# Helper: check sentence for verb-noun combinations
def match_verb_noun_in_proximity(doc, window=10):
    words = [token.lemma_ for token in doc if not token.is_stop and not token.is_space]
    for i, w in enumerate(words):
        if w in delete_verbs:
            for j in range(i + 1, min(i + window, len(words))):
                if words[j] in delete_nouns:
                    return True
        if w in delete_nouns:
            for j in range(i + 1, min(i + window, len(words))):
                if words[j] in delete_verbs:
                    return True
    return False

# Text preprocessing
def preprocess_text(text):
    return text.translate(str.maketrans("", "", string.punctuation))

# Analysis results
results = []

# Process each app
for pkg_name in pkg_list:
    file_path = os.path.join(txt_dir, f"{pkg_name}.txt")
    has_text = "Yes"
    contains_delete = False
    matched_sentences = []
    url_contains_delete = "No"

    if os.path.exists(file_path):
        print(f"[✓] Analyzing: {pkg_name}")
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                sentence = line.strip()
                if not sentence:
                    continue
                cleaned = preprocess_text(sentence)
                doc = nlp(cleaned.lower())
                lowered_text = cleaned.lower()

                if match_verb_noun_in_proximity(doc) and not any(neg in lowered_text for neg in negation_words):
                    matched_sentences.append(sentence)
                    contains_delete = True
    else:
        has_text = "No"
        print(f"[✗] No text for: {pkg_name}")

    # URL matching
    url = url_dict.get(pkg_name, "")
    if match_url_keywords(url):
        url_contains_delete = "Yes"
        if not contains_delete:
            matched_sentences.append(f"[From URL] {url}")
            contains_delete = False  # text must confirm it

    results.append({
        "pkg_name": pkg_name,
        "contains_delete": "Yes" if contains_delete else "No",
        "url_contains_delete": url_contains_delete
    })

# Merge back into original CSV
df_results = pd.DataFrame(results)
df_updated = pd.merge(df, df_results, on="pkg_name", how="left")

# Save back to original CSV
df_updated.to_csv(input_csv, index=False)
print(f"[✔] Updated results saved to: {input_csv}")
