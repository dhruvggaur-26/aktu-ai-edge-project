import json
from pathlib import Path
from langdetect import detect

INPUT_FILE = "data/processed/government_data_cleaned.jsonl"
OUTPUT_FILE = "data/processed/government_data_language.jsonl"

SUPPORTED_LANGUAGES = {"hi", "en", "mr"}

def detect_text_language(text, fallback_lang="hi"):
    if not text or not str(text).strip():
        return fallback_lang

    try:
        detected = detect(str(text))
        if detected in SUPPORTED_LANGUAGES:
            return detected
    except Exception:
        pass

    return fallback_lang

def process_language_detection():
    print("Loading cleaned dataset...")
    records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    print("Records loaded:", len(records))

    for record in records:
        source_lang = record.get("Language", "hi")
        detected_language = detect_text_language(
            record.get("Text", ""),
            fallback_lang=source_lang
        )
        # Declared 'Language' ko chhede bina sirf Detected_Language add karein
        record["Detected_Language"] = detected_language

    Path("data/processed").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("Language detection completed.")
    print("Language dataset saved to:", OUTPUT_FILE)

    language_counts = {}
    for record in records:
        lang = record["Detected_Language"]
        language_counts[lang] = language_counts.get(lang, 0) + 1

    print("\nDetected language distribution:")
    for lang, count in language_counts.items():
        print(f"{lang}: {count}")

if __name__ == "__main__":
    process_language_detection()