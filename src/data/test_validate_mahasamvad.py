import json
import re
from pathlib import Path


DATA_FILE = Path("data/raw/mahasamvad_marathi_raw.jsonl")
EXPECTED_RECORDS = 22

def load_records():
    records = []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def main():
    print("=" * 60)
    print("MAHASAMVAD MARATHI DATA VALIDATOR")
    print("=" * 60)

    records = load_records()

    passed = True

    # 1. Record count
    print(f"\nTotal records: {len(records)}")

    if len(records) == EXPECTED_RECORDS:
        print("Record count: PASS")
    else:
        print("Record count: FAIL")
        passed = False

    # 2. Required fields
    required_fields = [
        "id",
        "source",
        "language",
        "category",
        "title",
        "text",
        "source_url",
        "published_date",
        "date_collected",
    ]

    missing_fields = []

    for i, record in enumerate(records, start=1):
        for field in required_fields:
            if field not in record:
                missing_fields.append((i, field))

    if not missing_fields:
        print("Required fields: PASS")
    else:
        print("Required fields: FAIL")
        print(missing_fields)
        passed = False

    # 3. Duplicate IDs
    ids = [record.get("id") for record in records]

    if len(ids) == len(set(ids)):
        print("Duplicate IDs: PASS")
    else:
        print("Duplicate IDs: FAIL")
        passed = False

    # 4. Duplicate URLs
    urls = [record.get("source_url") for record in records]

    if len(urls) == len(set(urls)):
        print("Duplicate URLs: PASS")
    else:
        print("Duplicate URLs: FAIL")

        duplicates = [
            url for url in set(urls)
            if urls.count(url) > 1
        ]

        print("Duplicate URLs:", duplicates)
        passed = False

    # 5. Empty titles
    empty_titles = [
        record["id"]
        for record in records
        if not record.get("title", "").strip()
    ]

    if not empty_titles:
        print("Empty titles: PASS")
    else:
        print("Empty titles: FAIL")
        print(empty_titles)
        passed = False

    # 6. Empty text
    empty_text = [
        record["id"]
        for record in records
        if not record.get("text", "").strip()
    ]

    if not empty_text:
        print("Empty text: PASS")
    else:
        print("Empty text: FAIL")
        print(empty_text)
        passed = False

    # 7. Source
    wrong_source = [
        record["id"]
        for record in records
        if record.get("source") != "MahaSamvad"
    ]

    if not wrong_source:
        print("Source check: PASS")
    else:
        print("Source check: FAIL")
        print(wrong_source)
        passed = False

    # 8. Language
    wrong_language = [
        record["id"]
        for record in records
        if record.get("language") != "mr"
    ]

    if not wrong_language:
        print("Language check: PASS")
    else:
        print("Language check: FAIL")
        print(wrong_language)
        passed = False

    # 9. Category
    wrong_category = [
        record["id"]
        for record in records
        if record.get("category") != "government_news"
    ]

    if not wrong_category:
        print("Category check: PASS")
    else:
        print("Category check: FAIL")
        print(wrong_category)
        passed = False

    # 10. ID format
    wrong_ids = [
        record["id"]
        for record in records
        if not re.fullmatch(
            r"MahaSamvad_MR_\d{3}",
            record.get("id", "")
        )
    ]

    if not wrong_ids:
        print("ID format: PASS")
    else:
        print("ID format: FAIL")
        print(wrong_ids)
        passed = False

    # 11. URL check
    wrong_urls = [
        record["id"]
        for record in records
        if not record.get("source_url", "").startswith(
            "https://www.mahasamvad.in/"
        )
    ]

    if not wrong_urls:
        print("URL check: PASS")
    else:
        print("URL check: FAIL")
        print(wrong_urls)
        passed = False

    # 12. Marathi text check
    weak_marathi = []

    for record in records:
        text = record.get("text", "")

        devanagari_count = len(
            re.findall(r"[\u0900-\u097F]", text)
        )

        if devanagari_count < 100:
            weak_marathi.append(record["id"])

    if not weak_marathi:
        print("Marathi text check: PASS")
    else:
        print("Marathi text check: FAIL")
        print(weak_marathi)
        passed = False

    # Final result
    print("\n" + "=" * 60)

    if passed:
        print("OVERALL STATUS: PASS")
    else:
        print("OVERALL STATUS: FAIL")

    print("=" * 60)


if __name__ == "__main__":
    main()