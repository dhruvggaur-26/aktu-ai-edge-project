import json
import re
from pathlib import Path


INPUT_FILE = Path(
    "data/raw/lokbhavan_marathi_raw.jsonl"
)

EXPECTED_RECORDS = 280

REQUIRED_FIELDS = [
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


def validate():
    print("=" * 50)
    print("LOK BHAVAN MARATHI DATA VALIDATOR")
    print("=" * 50)

    if not INPUT_FILE.exists():
        print(f"\nERROR: File not found:")
        print(INPUT_FILE)
        return

    records = []

    # -----------------------------
    # LOAD JSONL
    # -----------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError as e:
                print(
                    f"\nInvalid JSON at line {line_number}:"
                )
                print(e)
                return

            records.append(record)

    print(
        f"\nTotal records: {len(records)}"
    )

    # -----------------------------
    # RECORD COUNT
    # -----------------------------

    if len(records) == EXPECTED_RECORDS:
        print("Record count: PASS")
    else:
        print(
            f"Record count: FAIL "
            f"(expected {EXPECTED_RECORDS}, "
            f"found {len(records)})"
        )

    # -----------------------------
    # REQUIRED FIELDS
    # -----------------------------

    missing_fields = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        for field in REQUIRED_FIELDS:

            if field not in record:
                missing_fields.append(
                    (index, field)
                )

    if not missing_fields:
        print("Required fields: PASS")
    else:
        print("Required fields: FAIL")

        for item in missing_fields:
            print(
                f"  Record {item[0]} "
                f"missing: {item[1]}"
            )

    # -----------------------------
    # DUPLICATE IDS
    # -----------------------------

    ids = [
        record.get("id")
        for record in records
    ]

    duplicate_ids = {
        item
        for item in ids
        if item is not None
        and ids.count(item) > 1
    }

    if not duplicate_ids:
        print("Duplicate IDs: PASS")
    else:
        print("Duplicate IDs: FAIL")

        for item in duplicate_ids:
            print(
                f"  Duplicate ID: {item}"
            )

    # -----------------------------
    # DUPLICATE URLS
    # -----------------------------

    urls = [
        record.get("source_url")
        for record in records
    ]

    duplicate_urls = {
        item
        for item in urls
        if item is not None
        and urls.count(item) > 1
    }

    if not duplicate_urls:
        print("Duplicate URLs: PASS")
    else:
        print("Duplicate URLs: FAIL")

        for item in duplicate_urls:
            print(
                f"  Duplicate URL: {item}"
            )

    # -----------------------------
    # EMPTY TITLES
    # -----------------------------

    empty_titles = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        if not str(
            record.get("title", "")
        ).strip():

            empty_titles.append(index)

    if not empty_titles:
        print("Empty titles: PASS")
    else:
        print("Empty titles: FAIL")

        for index in empty_titles:
            print(
                f"  Empty title: Record {index}"
            )

    # -----------------------------
    # EMPTY TEXT
    # -----------------------------

    empty_text = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        if not str(
            record.get("text", "")
        ).strip():

            empty_text.append(index)

    if not empty_text:
        print("Empty text: PASS")
    else:
        print("Empty text: FAIL")

        for index in empty_text:
            print(
                f"  Empty text: Record {index}"
            )

    # -----------------------------
    # SOURCE CHECK
    # -----------------------------

    wrong_source = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        if record.get("source") != (
            "Lok Bhavan Maharashtra"
        ):
            wrong_source.append(index)

    if not wrong_source:
        print("Source check: PASS")
    else:
        print("Source check: FAIL")

        for index in wrong_source:
            print(
                f"  Wrong source: Record {index}"
            )

    # -----------------------------
    # LANGUAGE CHECK
    # -----------------------------

    wrong_language = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        if record.get("language") != "mr":
            wrong_language.append(index)

    if not wrong_language:
        print("Language check: PASS")
    else:
        print("Language check: FAIL")

        for index in wrong_language:
            print(
                f"  Wrong language: Record {index}"
            )

    # -----------------------------
    # CATEGORY CHECK
    # -----------------------------

    wrong_category = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        if record.get("category") != (
            "government_press_release"
        ):
            wrong_category.append(index)

    if not wrong_category:
        print("Category check: PASS")
    else:
        print("Category check: FAIL")

        for index in wrong_category:
            print(
                f"  Wrong category: Record {index}"
            )

    # -----------------------------
    # ID FORMAT CHECK
    # -----------------------------

    invalid_ids = []

    id_pattern = re.compile(
        r"^LokBhavan_MR_\d{3}$"
    )

    for index, record in enumerate(
        records,
        start=1,
    ):

        record_id = record.get("id", "")

        if not id_pattern.match(
            str(record_id)
        ):
            invalid_ids.append(
                (index, record_id)
            )

    if not invalid_ids:
        print("ID format: PASS")
    else:
        print("ID format: FAIL")

        for index, record_id in invalid_ids:
            print(
                f"  Record {index}: "
                f"{record_id}"
            )

    # -----------------------------
    # URL CHECK
    # -----------------------------

    invalid_urls = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        url = str(
            record.get("source_url", "")
        )

        if not url.startswith(
            "https://lokbhavan.maharashtra.gov.in/"
        ):
            invalid_urls.append(
                (index, url)
            )

    if not invalid_urls:
        print("URL check: PASS")
    else:
        print("URL check: FAIL")

        for index, url in invalid_urls:
            print(
                f"  Record {index}: {url}"
            )

    # -----------------------------
    # MARATHI TEXT CHECK
    # -----------------------------

    non_marathi_records = []

    for index, record in enumerate(
        records,
        start=1,
    ):

        text = (
            str(record.get("title", ""))
            + " "
            + str(record.get("text", ""))
        )

        devanagari_count = len(
            re.findall(
                r"[\u0900-\u097F]",
                text,
            )
        )

        if devanagari_count < 100:
            non_marathi_records.append(
                index
            )

    if not non_marathi_records:
        print("Marathi text check: PASS")
    else:
        print(
            "Marathi text check: FAIL"
        )

        for index in non_marathi_records:
            print(
                f"  Possible non-Marathi "
                f"record: {index}"
            )

    # -----------------------------
    # FINAL RESULT
    # -----------------------------

    checks = [
        len(records) == EXPECTED_RECORDS,
        not missing_fields,
        not duplicate_ids,
        not duplicate_urls,
        not empty_titles,
        not empty_text,
        not wrong_source,
        not wrong_language,
        not wrong_category,
        not invalid_ids,
        not invalid_urls,
        not non_marathi_records,
    ]

    print("\n" + "=" * 50)

    if all(checks):
        print("OVERALL STATUS: PASS")
    else:
        print("OVERALL STATUS: FAIL")

    print("=" * 50)


if __name__ == "__main__":
    validate()