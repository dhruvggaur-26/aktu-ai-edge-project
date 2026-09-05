import json
import re
from pathlib import Path


INPUT_FILE = "data/processed/government_data_combined.jsonl"
OUTPUT_FILE = "data/processed/government_data_cleaned.jsonl"


TEXT_FIELDS = [
    "Title",
    "Text",
    "Source",
    "Language",
    "Category",
    "Department",
]


def clean_text(text):
    """
    Normalize text without changing its actual meaning.
    """

    if text is None:
        return ""

    text = str(text)

    # Normalize multiple spaces and line breaks
    text = re.sub(r"\s+", " ", text)

    # Remove unnecessary spaces around punctuation
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def clean_records():

    print("Loading combined dataset...")

    records = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    print(
        "Records loaded:",
        len(records)
    )

    cleaned_records = []

    for record in records:

        cleaned_record = record.copy()

        for field in TEXT_FIELDS:

            if field in cleaned_record:
                cleaned_record[field] = clean_text(
                    cleaned_record[field]
                )

        cleaned_records.append(
            cleaned_record
        )

    # Create output directory
    Path(
        "data/processed"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned dataset
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in cleaned_records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print(
        "Cleaned dataset saved to:",
        OUTPUT_FILE
    )

    print(
        "Cleaned records:",
        len(cleaned_records)
    )


if __name__ == "__main__":
    clean_records()