import pandas as pd

RAW_FILE = "data/raw/government_data_raw.xlsx"
PROCESSED_FILE = "data/processed/government_data_cleaned.xlsx"

df = pd.read_excel(RAW_FILE)
TEXT_COLUMNS = ["Title", "Text", "Source", "Language", "Category", "Department"]

for column in TEXT_COLUMNS:
    df[column] = (
        df[column]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
from pathlib import Path

Path("data/processed").mkdir(parents=True, exist_ok=True)

df.to_excel(PROCESSED_FILE, index=False)

print("Cleaned dataset saved to:", PROCESSED_FILE)