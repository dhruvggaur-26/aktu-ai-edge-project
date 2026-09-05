import json


FINAL_FILE = "data/final/government_data_tokenized.jsonl"


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
    "Detected_Language",
    "Tokens",
]


def load_records():

    records = []

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def run_quality_check():

    records = load_records()

    print(
        "Total records:",
        len(records)
    )

    # -----------------------------------------
    # Required fields
    # -----------------------------------------

    missing_fields = []

    for record in records:

        for field in REQUIRED_FIELDS:

            if field not in record:

                missing_fields.append(
                    (
                        record.get("ID"),
                        field
                    )
                )

    if not missing_fields:

        print(
            "All required fields are present."
        )

    else:

        print(
            "Missing fields:",
            missing_fields
        )

    # -----------------------------------------
    # Duplicate IDs
    # -----------------------------------------

    ids = [
        record.get("ID")
        for record in records
    ]

    duplicate_ids = [
        record_id
        for record_id in set(ids)
        if ids.count(record_id) > 1
    ]

    if not duplicate_ids:

        print(
            "No duplicate IDs found."
        )

    else:

        print(
            "Duplicate IDs found:",
            duplicate_ids
        )

    # -----------------------------------------
    # Empty text
    # -----------------------------------------

    empty_text = [
        record.get("ID")
        for record in records
        if not str(
            record.get("Text", "")
        ).strip()
    ]

    if not empty_text:

        print(
            "No empty text records found."
        )

    else:

        print(
            "Empty text records:",
            empty_text
        )

    # -----------------------------------------
    # Empty tokens
    # -----------------------------------------

    empty_tokens = [
        record.get("ID")
        for record in records
        if not record.get("Tokens")
    ]

    if not empty_tokens:

        print(
            "No empty token lists found."
        )

    else:

        print(
            "Empty token lists:",
            empty_tokens
        )

    # -----------------------------------------
    # Language consistency
    # -----------------------------------------

    language_mismatch = []

    for record in records:

        if (
            record.get("Language")
            != record.get("Detected_Language")
        ):

            language_mismatch.append(
                (
                    record.get("ID"),
                    record.get("Language"),
                    record.get("Detected_Language")
                )
            )

    if not language_mismatch:

        print(
            "No language mismatches found."
        )

    else:

        print(
            "Language mismatches:",
            language_mismatch
        )

    # -----------------------------------------
    # Token statistics
    # -----------------------------------------

    token_counts = [
        len(record["Tokens"])
        for record in records
        if isinstance(
            record.get("Tokens"),
            list
        )
    ]

    if token_counts:

        print("\nToken statistics:")

        print(
            "Minimum tokens:",
            min(token_counts)
        )

        print(
            "Maximum tokens:",
            max(token_counts)
        )

        print(
            "Average tokens:",
            round(
                sum(token_counts)
                / len(token_counts),
                2
            )
        )

    print("\nQuality check completed.")


if __name__ == "__main__":
    run_quality_check()