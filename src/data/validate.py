import json
import pandas as pd


RAW_FILE = "data/processed/government_data_combined.jsonl"

REQUIRED_COLUMNS = [
    "ID",
    "Title",
    "Text",
    "Source",
    "Url",
    "Language",
    "Category",
    "Department",
    "Date_collected",
]


# Load JSONL dataset
records = []

with open(RAW_FILE, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            records.append(json.loads(line))

df = pd.DataFrame(records)

print("Total records:", len(df))


# 1. Check required columns
missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if not missing_columns:
    print("All required columns are present.")
else:
    print("Missing columns:", missing_columns)


# 2. Check duplicate IDs
duplicate_ids = df[df["ID"].duplicated(keep=False)]

if duplicate_ids.empty:
    print("No duplicate IDs found.")
else:
    print("Duplicate IDs found:")
    print(duplicate_ids["ID"].tolist())


# 3. Check missing values
missing_values = df[REQUIRED_COLUMNS].isnull().sum()

if missing_values.sum() == 0:
    print("No missing values found.")
else:
    print("Missing values found:")
    print(missing_values[missing_values > 0])


# 4. Check URL format
invalid_urls = df[
    ~df["Url"].astype(str).str.startswith(("http://", "https://"))
]

if invalid_urls.empty:
    print("All URLs have a valid format.")
else:
    print("Invalid URLs found:")
    print(invalid_urls[["ID", "Url"]])


# 5. Check dates
invalid_dates = pd.to_datetime(
    df["Date_collected"],
    errors="coerce"
).isnull()

if not invalid_dates.any():
    print("All dates are valid.")
else:
    print("Invalid dates found:")
    print(df.loc[invalid_dates, ["ID", "Date_collected"]])