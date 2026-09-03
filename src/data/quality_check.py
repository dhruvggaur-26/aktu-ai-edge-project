import json

FINAL_FILE = "data/final/government_data_tokenized.jsonl"

with open(FINAL_FILE, "r", encoding="utf-8") as file:
    rows = [json.loads(line) for line in file]

print("Total records:", len(rows))

required_fields = [
    "ID",
    "Title",
    "Text",
    "Source",
    "Url",
    "Language",
    "Category",
    "Department",
    "Date_collected",
    "Tokens",
]

missing_fields = []

for row in rows:
    for field in required_fields:
        if field not in row:
            missing_fields.append((row.get("ID"), field))

if not missing_fields:
    print("All required fields are present.")
else:
    print("Missing fields:", missing_fields)

duplicate_ids = [
    row["ID"]
    for row in rows
    if sum(r["ID"] == row["ID"] for r in rows) > 1
]

if not duplicate_ids:
    print("No duplicate IDs found.")
else:
    print("Duplicate IDs found:", set(duplicate_ids))

empty_text = [
    row["ID"]
    for row in rows
    if not str(row["Text"]).strip()
]

if not empty_text:
    print("No empty text records found.")
else:
    print("Empty text records:", empty_text)

empty_tokens = [
    row["ID"]
    for row in rows
    if not row["Tokens"]
]

if not empty_tokens:
    print("No empty token lists found.")
else:
    print("Empty token lists:", empty_tokens)

print("\nToken counts:")

for row in rows:
    print(f"{row['ID']}: {len(row['Tokens'])} tokens")
