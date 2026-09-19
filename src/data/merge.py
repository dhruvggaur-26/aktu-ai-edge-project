import json
from pathlib import Path

import pandas as pd


# Input files
MYScheme_FILE = "data/raw/government_data_raw.xlsx"
PIB_FILE = "data/raw/pib_raw.jsonl"
PMINDIA_FILE = "data/raw/pmindia_hindi_raw.jsonl"
NEWSONAIR_FILE = "data/raw/newsonair_hindi_raw.jsonl"
DDNEWS_FILE = "data/raw/ddnews_hindi_raw.jsonl"


# Output file
OUTPUT_FILE = "data/processed/government_data_combined.jsonl"


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


def load_myscheme():
    df = pd.read_excel(MYScheme_FILE)

    # Convert pandas Timestamp values into JSON-compatible strings
    if "Date_collected" in df.columns:
        df["Date_collected"] = (
            pd.to_datetime(
                df["Date_collected"],
                errors="coerce"
            )
            .dt.strftime("%Y-%m-%d")
        )

    return df.to_dict(orient="records")


def load_jsonl(file_path):
    records = []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def validate_schema(records, source_name):

    for record in records:

        missing_fields = [
            field
            for field in REQUIRED_FIELDS
            if field not in record
        ]

        if missing_fields:
            raise ValueError(
                f"{source_name} record "
                f"{record.get('ID')} is missing: "
                f"{missing_fields}"
            )


def merge_datasets():

    # -------------------------------------------------
    # Load myScheme
    # -------------------------------------------------

    print("Loading myScheme dataset...")

    myscheme_records = load_myscheme()

    print(
        "myScheme records:",
        len(myscheme_records)
    )


    # -------------------------------------------------
    # Load PIB
    # -------------------------------------------------

    print("\nLoading PIB dataset...")

    pib_records = load_jsonl(PIB_FILE)

    print(
        "PIB records:",
        len(pib_records)
    )


    # -------------------------------------------------
    # Load PM India
    # -------------------------------------------------

    print("\nLoading PM India dataset...")

    pmindia_records = load_jsonl(PMINDIA_FILE)

    print(
        "PM India records:",
        len(pmindia_records)
    )


    # -------------------------------------------------
    # Load News On AIR
    # -------------------------------------------------

    print("\nLoading News On AIR dataset...")

    newsonair_records = load_jsonl(NEWSONAIR_FILE)

    print(
        "News On AIR records:",
        len(newsonair_records)
    )


    # -------------------------------------------------
    # Load DD News
    # -------------------------------------------------

    print("\nLoading DD News dataset...")

    ddnews_records = load_jsonl(DDNEWS_FILE)

    print(
        "DD News records:",
        len(ddnews_records)
    )


    # -------------------------------------------------
    # Validate schemas
    # -------------------------------------------------

    print("\nValidating schemas...")

    validate_schema(
        myscheme_records,
        "myScheme"
    )

    validate_schema(
        pib_records,
        "PIB"
    )

    validate_schema(
        pmindia_records,
        "PM India"
    )

    validate_schema(
        newsonair_records,
        "News On AIR"
    )

    validate_schema(
        ddnews_records,
        "DD News"
    )

    print("Schema validation passed.")


    # -------------------------------------------------
    # Combine all datasets
    # -------------------------------------------------

    combined_records = (
        myscheme_records
        + pib_records
        + pmindia_records
        + newsonair_records
        + ddnews_records
    )


    # -------------------------------------------------
    # Check duplicate IDs
    # -------------------------------------------------

    ids = [
        record["ID"]
        for record in combined_records
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate IDs found in combined dataset."
        )


    # -------------------------------------------------
    # Print combined dataset statistics
    # -------------------------------------------------

    print("\nCombined records:")

    print(
        "Total:",
        len(combined_records)
    )

    print(
        "Unique IDs:",
        len(set(ids))
    )


    # -------------------------------------------------
    # Create output directory
    # -------------------------------------------------

    Path(
        "data/processed"
    ).mkdir(
        parents=True,
        exist_ok=True
    )


    # -------------------------------------------------
    # Save combined dataset
    # -------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in combined_records:

            # Keep only the common schema
            clean_record = {
                field: record.get(field, "")
                for field in REQUIRED_FIELDS
            }

            file.write(
                json.dumps(
                    clean_record,
                    ensure_ascii=False
                ) + "\n"
            )


    print(
        "\nCombined dataset saved to:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    merge_datasets()