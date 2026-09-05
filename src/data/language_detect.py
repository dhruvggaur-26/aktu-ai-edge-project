import json
from pathlib import Path

from langdetect import detect


INPUT_FILE = "data/processed/government_data_cleaned.jsonl"
OUTPUT_FILE = "data/processed/government_data_language.jsonl"


def detect_language(text):
    """
    Detect the language of the given text.
    """

    if not text or not str(text).strip():
        return "unknown"

    try:
        return detect(str(text))
    except Exception:
        return "unknown"


def process_language_detection():

    print("Loading cleaned dataset...")

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

    for record in records:

        detected_language = detect_language(
            record.get("Text", "")
        )

        record["Detected_Language"] = detected_language

    # Create output directory
    Path(
        "data/processed"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    # Save result
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print(
        "Language detection completed."
    )

    print(
        "Language dataset saved to:",
        OUTPUT_FILE
    )

    # Show language distribution
    language_counts = {}

    for record in records:

        language = record[
            "Detected_Language"
        ]

        language_counts[language] = (
            language_counts.get(language, 0) + 1
        )

    print("\nDetected language distribution:")

    for language, count in language_counts.items():

        print(
            f"{language}: {count}"
        )


if __name__ == "__main__":
    process_language_detection()