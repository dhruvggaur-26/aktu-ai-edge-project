import json
from pathlib import Path

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

def run_quality_check():
    file_path = Path(FINAL_FILE)
    if not file_path.exists():
        print(f"Error: File not found at {FINAL_FILE}")
        return

    records = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    total_records = len(records)
    print(f"Total records: {total_records}")

    # 1. Check required fields
    missing_fields = set()
    for record in records:
        for field in REQUIRED_FIELDS:
            if field not in record:
                missing_fields.add(field)

    if not missing_fields:
        print("All required fields are present.")
    else:
        print(f"Missing fields detected: {list(missing_fields)}")

    # 2. Check duplicate IDs
    seen_ids = set()
    duplicates = set()
    for record in records:
        rec_id = record.get("ID")
        if rec_id in seen_ids:
            duplicates.add(rec_id)
        seen_ids.add(rec_id)

    if not duplicates:
        print("No duplicate IDs found.")
    else:
        print(f"Duplicate IDs found: {list(duplicates)}")

    # 3. Check empty text records
    empty_texts = [r.get("ID") for r in records if not str(r.get("Text", "")).strip()]
    if not empty_texts:
        print("No empty text records found.")
    else:
        print(f"Empty text records found: {empty_texts}")

    # 4. Check empty token lists
    empty_tokens = [r.get("ID") for r in records if not r.get("Tokens")]
    if not empty_tokens:
        print("No empty token lists found.")
    else:
        print(f"Empty token lists found: {empty_tokens}")

    # 5. Language Detection Audit (Informational Reporting)
    language_mismatch = []
    for record in records:
        declared = record.get("Language")
        detected = record.get("Detected_Language")
        if declared and detected and declared != detected:
            language_mismatch.append((record.get("ID"), declared, detected))

    if language_mismatch:
        print(
            f"\nLanguage Detection Audit: "
            f"{len(language_mismatch)} record(s) flagged."
        )
        for rec_id, declared, detected in language_mismatch:
            print(
                f"  - {rec_id}: "
                f"Declared='{declared}', "
                f"Detected='{detected}'"
            )
        print(
            "  -> Status: INFORMATIONAL "
            "(mixed-language, embedded content, or possible detection anomaly)"
        )
    else:
        print("\nLanguage Detection Audit: No anomalies found.")

    # 6. Token statistics
    token_lengths = [len(r.get("Tokens", [])) for r in records]
    if token_lengths:
        min_tokens = min(token_lengths)
        max_tokens = max(token_lengths)
        avg_tokens = sum(token_lengths) / len(token_lengths)

        print("\nToken statistics:")
        print(f"Minimum tokens: {min_tokens}")
        print(f"Maximum tokens: {max_tokens}")
        print(f"Average tokens: {avg_tokens:.2f}")

    print("\nQuality check completed.")

if __name__ == "__main__":
    run_quality_check()