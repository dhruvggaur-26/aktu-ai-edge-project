import pandas as pd

RAW_FILE = "data/raw/government_data_raw.xlsx"
df = pd.read_excel(RAW_FILE)
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

missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    print("Missing columns:", missing_columns)
else:
    print("All required columns are present.")
duplicate_ids = df[df["ID"].duplicated(keep=False)]

if duplicate_ids.empty:
    print("No duplicate IDs found.")
else:
    print("Duplicate IDs found:")
    print(duplicate_ids["ID"].tolist())
missing_values = df[REQUIRED_COLUMNS].isnull().sum()

if missing_values.sum() == 0:
    print("No missing values found.")
else:
    print("Missing values found:")
    print(missing_values[missing_values > 0])
invalid_urls = df[
    ~df["Url"].astype(str).str.startswith(("http://", "https://"))
]

if invalid_urls.empty:
    print("All URLs have a valid format.")
else:
    print("Invalid URLs found:")
    print(invalid_urls[["ID", "Url"]])
invalid_dates = pd.to_datetime(
    df["Date_collected"],
    errors="coerce"
).isnull()

if not invalid_dates.any():
    print("All dates are valid.")
else:
    print("Invalid dates found:")
    print(df.loc[invalid_dates, ["ID", "Date_collected"]])


