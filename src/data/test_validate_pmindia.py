import json
from urllib.parse import urlparse


FILE = "data/raw/pmindia_hindi_raw.jsonl"

REQUIRED_FIELDS = [
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


records = []

with open(FILE, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            records.append(json.loads(line))


print("=" * 60)
print("PM INDIA HINDI DATA VALIDATION")
print("=" * 60)

print("Total records:", len(records))


# 1. Required fields
missing_fields = []

for i, record in enumerate(records, start=1):
    for field in REQUIRED_FIELDS:
        if field not in record:
            missing_fields.append((i, field))

if not missing_fields:
    print("Required fields: PASS")
else:
    print("Required fields: FAIL")
    print("Missing:", missing_fields)


# 2. Duplicate IDs
ids = [record.get("ID") for record in records]
duplicate_ids = {
    item for item in ids
    if ids.count(item) > 1
}

if not duplicate_ids:
    print("Duplicate IDs: PASS")
else:
    print("Duplicate IDs: FAIL")
    print("Duplicates:", duplicate_ids)


# 3. Duplicate URLs
urls = [record.get("Url") for record in records]
duplicate_urls = {
    item for item in urls
    if urls.count(item) > 1
}

if not duplicate_urls:
    print("Duplicate URLs: PASS")
else:
    print("Duplicate URLs: FAIL")
    print("Duplicates:", duplicate_urls)


# 4. Empty Title/Text
empty_titles = [
    record.get("ID")
    for record in records
    if not str(record.get("Title", "")).strip()
]

empty_text = [
    record.get("ID")
    for record in records
    if not str(record.get("Text", "")).strip()
]

print("Empty Titles:", len(empty_titles))
print("Empty Text:", len(empty_text))


# 5. Language
wrong_language = [
    record.get("ID")
    for record in records
    if record.get("Language") != "hi"
]

if not wrong_language:
    print("Language (hi): PASS")
else:
    print("Language (hi): FAIL")
    print("Wrong records:", wrong_language)


# 6. Source
wrong_source = [
    record.get("ID")
    for record in records
    if record.get("Source") != "PM India"
]

if not wrong_source:
    print("Source (PM India): PASS")
else:
    print("Source (PM India): FAIL")
    print("Wrong records:", wrong_source)


# 7. Category
wrong_category = [
    record.get("ID")
    for record in records
    if record.get("Category") != "news"
]

if not wrong_category:
    print("Category (news): PASS")
else:
    print("Category (news): FAIL")
    print("Wrong records:", wrong_category)


# 8. URL validation
invalid_urls = []

for record in records:
    url = record.get("Url", "")

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or parsed.netloc != "www.pmindia.gov.in"
        or not parsed.path.startswith("/hi/news_updates/")
    ):
        invalid_urls.append(record.get("ID"))

if not invalid_urls:
    print("PM India URLs: PASS")
else:
    print("PM India URLs: FAIL")
    print("Invalid records:", invalid_urls)


# 9. Final summary
print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

if (
    len(records) > 0
    and not missing_fields
    and not duplicate_ids
    and not duplicate_urls
    and not empty_titles
    and not empty_text
    and not wrong_language
    and not wrong_source
    and not wrong_category
    and not invalid_urls
):
    print("Overall Status: PASS")
else:
    print("Overall Status: REVIEW REQUIRED")