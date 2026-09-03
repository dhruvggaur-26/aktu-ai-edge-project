import pandas as pd
from transformers import AutoTokenizer

CLEANED_FILE = "data/processed/government_data_cleaned.xlsx"
MODEL_PATH = "models/pytorch/indic_ner_final/indic_ner_final"

df = pd.read_excel(CLEANED_FILE)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
def tokenize_text(text):
    return tokenizer.tokenize(text)


df["Tokens"] = df["Text"].apply(tokenize_text)

print("\nFull dataset tokenization completed.")

for _, row in df.iterrows():
    print(f"{row['ID']}: {len(row['Tokens'])} tokens")
import json

FINAL_FILE = "data/final/government_data_tokenized.jsonl"

with open(FINAL_FILE, "w", encoding="utf-8") as file:
    for _, row in df.iterrows():
        record = row.to_dict()

        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                record[key] = value.strftime("%Y-%m-%d")

        file.write(json.dumps(record, ensure_ascii=False) + "\n")

print("\nFinal tokenized dataset saved to:", FINAL_FILE)