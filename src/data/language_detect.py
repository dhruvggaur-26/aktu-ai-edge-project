import pandas as pd
from langdetect import detect

CLEANED_FILE = "data/processed/government_data_cleaned.xlsx"

df = pd.read_excel(CLEANED_FILE)
detected_languages = []

for text in df["Text"]:
    try:
        detected_languages.append(detect(text))
    except Exception:
        detected_languages.append("unknown")

df["Detected_Language"] = detected_languages

print(df[["ID", "Language", "Detected_Language"]])