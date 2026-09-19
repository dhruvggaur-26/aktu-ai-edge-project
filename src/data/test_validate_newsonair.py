import json
from urllib.parse import urlparse

RAW_FILE = "data/raw/newsonair_hindi_raw.jsonl"

REQUIRED_FIELDS = [
    "ID",
    "Title",
    "Text",
    "Source",
    "Url",
    "Language",
    "Category",
    "Department",
    "Date_collected"
]

records = []

with open(RAW_FILE, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            print(f"Invalid JSON at line {line_number}: {error}")

print("Total records:", len(records))

errors = []

# Required fields
for index, record in enumerate(records, start=1):
    missing = [
        field for field in REQUIRED_FIELDS
        if field not in record
    ]

    if missing:
        errors.append(
            f"Record {index}: missing fields {missing}"
        )

# Duplicate IDs
ids = [record.get("ID") for record in records]

if len(ids) != len(set(ids)):
    errors.append("Duplicate IDs found")

# Duplicate URLs
urls = [record.get("Url") for record in records]

if len(urls) != len(set(urls)):
    errors.append("Duplicate URLs found")

# Empty title/text
for index, record in enumerate(records, start=1):

    if not str(record.get("Title", "")).strip():
        errors.append(f"Record {index}: empty title")

    if not str(record.get("Text", "")).strip():
        errors.append(f"Record {index}: empty text")

# Source checks
for index, record in enumerate(records, start=1):

    if record.get("Source") != "News On AIR":
        errors.append(
            f"Record {index}: incorrect source"
        )

    if record.get("Language") != "hi":
        errors.append(
            f"Record {index}: incorrect language"
        )

    if record.get("Category") != "news":
        errors.append(
            f"Record {index}: incorrect category"
        )

# URL checks
for index, record in enumerate(records, start=1):

    url = record.get("Url", "")

    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        errors.append(
            f"Record {index}: invalid URL"
        )

    if parsed.netloc not in ["newsonair.gov.in", "www.newsonair.gov.in"]:
        errors.append(
            f"Record {index}: unexpected URL host"
        )

print("\n--- VALIDATION RESULTS ---")

if errors:
    print("Status: FAIL")
    print("\nErrors:")

    for error in errors:
        print("-", error)

else:
    print("Status: PASS")
    print("All required fields present")
    print("No duplicate IDs")
    print("No duplicate URLs")
    print("No empty titles")
    print("No empty text")
    print("Language check: PASS")
    print("Source check: PASS")
    print("Category check: PASS")
    print("URL check: PASS")

print("\nOverall Status:", "PASS" if not errors else "FAIL")