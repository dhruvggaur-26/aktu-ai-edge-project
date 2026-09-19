import json
from pathlib import Path
from urllib.parse import urlparse

FILE = Path("data/raw/ddnews_hindi_raw.jsonl")

required_fields = [
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
errors = []

if not FILE.exists():
    print("❌ File not found:", FILE)
    raise SystemExit(1)

with FILE.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            record = json.loads(line)
            records.append(record)
        except json.JSONDecodeError as e:
            errors.append(f"Line {line_no}: Invalid JSON - {e}")

print("Total records:", len(records))
print()

# Required fields
for i, record in enumerate(records, start=1):
    for field in required_fields:
        if field not in record:
            errors.append(
                f"Record {i} ({record.get('ID', 'UNKNOWN')}): "
                f"Missing field '{field}'"
            )

# Duplicate IDs
ids = [r.get("ID") for r in records]
duplicate_ids = {x for x in ids if ids.count(x) > 1}

if duplicate_ids:
    errors.append(f"Duplicate IDs: {duplicate_ids}")

# Duplicate URLs
urls = [r.get("Url") for r in records]
duplicate_urls = {x for x in urls if urls.count(x) > 1}

if duplicate_urls:
    errors.append(f"Duplicate URLs: {duplicate_urls}")

# Empty fields
for i, record in enumerate(records, start=1):
    if not str(record.get("Title", "")).strip():
        errors.append(f"Record {i}: Empty Title")

    if not str(record.get("Text", "")).strip():
        errors.append(f"Record {i}: Empty Text")

# Source
source_errors = [
    r.get("ID")
    for r in records
    if r.get("Source") != "DD News"
]

if source_errors:
    errors.append(
        f"Source check failed for: {source_errors}"
    )

# Language
language_errors = [
    r.get("ID")
    for r in records
    if r.get("Language") != "hi"
]

if language_errors:
    errors.append(
        f"Language check failed for: {language_errors}"
    )

# Category
category_errors = [
    r.get("ID")
    for r in records
    if r.get("Category") != "news"
]

if category_errors:
    errors.append(
        f"Category check failed for: {category_errors}"
    )

# URL
for record in records:
    url = record.get("Url", "")
    parsed = urlparse(url)

    if parsed.scheme != "https" or parsed.netloc != "ddnews.gov.in":
        errors.append(
            f"Invalid DD News URL: {record.get('ID')} -> {url}"
        )

print("--- VALIDATION RESULTS ---")

if errors:
    print("Status: FAIL")
    print()

    for error in errors:
        print("❌", error)

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

print()

if errors:
    print("Overall Status: FAIL")
else:
    print("Overall Status: PASS")