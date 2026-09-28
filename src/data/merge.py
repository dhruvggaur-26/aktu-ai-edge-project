import json
from pathlib import Path
from datetime import date
import pandas as pd

RAW_FILES = [
    {"path": "data/raw/government_data_raw.xlsx", "type": "excel"},
    {"path": "data/raw/pib_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/pmindia_hindi_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/newsonair_hindi_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/ddnews_hindi_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/myscheme_english_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/pib_english_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/pmindia_english_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/newsonair_english_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/lokbhavan_marathi_raw.jsonl", "type": "jsonl"},
    {"path": "data/raw/mahasamvad_marathi_raw.jsonl", "type": "jsonl"},
]

OUTPUT_FILE = Path("data/processed/government_data_combined.jsonl")

REQUIRED_FIELDS = [
    "ID", "Title", "Text", "Source", "Url", 
    "Language", "Category", "Department", "Date_collected"
]

def parse_date_to_iso(date_str):
    """
    Kisi bhi textual date format (e.g. 'September 17, 2026 8:11 AM')
    ko standard 'YYYY-MM-DD' mein convert karta hai.
    Agar date empty ya invalid ho, toh fallback aaj ki date deta hai.
    """
    if not date_str or not str(date_str).strip():
        return str(date.today())
    
    try:
        parsed = pd.to_datetime(str(date_str).strip(), errors="coerce")
        if pd.notnull(parsed):
            return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass
    
    return str(date.today())

def normalize_dict(record):
    record_id = record.get("ID") or record.get("id") or ""
    title = record.get("Title") or record.get("title") or ""
    text = record.get("Text") or record.get("text") or ""
    source = record.get("Source") or record.get("source") or ""
    url = record.get("Url") or record.get("source_url") or record.get("URL") or ""
    
    lang = str(record.get("Language") or record.get("language") or "hi").strip().lower()
    if lang == "hindi":
        lang = "hi"
    elif lang == "english":
        lang = "en"
    elif lang == "marathi":
        lang = "mr"

    category = record.get("Category") or record.get("category") or "news"
    dept = record.get("Department") or record.get("department") or record.get("nodal_department") or ""
    
    raw_date = (
        record.get("Date_collected") 
        or record.get("Date") 
        or record.get("date") 
        or record.get("Publication_Date") 
        or ""
    )
    date_col = parse_date_to_iso(raw_date)

    return {
        "ID": str(record_id).strip(),
        "Title": str(title).strip(),
        "Text": str(text).strip(),
        "Source": str(source).strip(),
        "Url": str(url).strip(),
        "Language": lang,
        "Category": str(category).strip(),
        "Department": str(dept).strip(),
        "Date_collected": date_col
    }

def merge_all_sources():
    combined_records = []
    seen_ids = set()

    for item in RAW_FILES:
        file_path = Path(item["path"])
        if not file_path.exists():
            print(f"[SKIP] File not found: {file_path}")
            continue

        print(f"Loading: {file_path.name}")
        records_to_process = []

        if item["type"] == "excel":
            df = pd.read_excel(file_path)
            if "Date_collected" in df.columns:
                df["Date_collected"] = pd.to_datetime(df["Date_collected"], errors="coerce").dt.strftime("%Y-%m-%d")
            records_to_process = df.to_dict(orient="records")
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records_to_process.append(json.loads(line))

        for raw_rec in records_to_process:
            clean_rec = normalize_dict(raw_rec)
            
            if not clean_rec["ID"] or not clean_rec["Text"]:
                continue

            if clean_rec["ID"] in seen_ids:
                print(f"[DUPLICATE ID SKIPPED]: {clean_rec['ID']}")
                continue

            seen_ids.add(clean_rec["ID"])
            combined_records.append(clean_rec)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for rec in combined_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("\n=================================")
    print(f"Total Combined Records: {len(combined_records)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=================================")

if __name__ == "__main__":
    merge_all_sources()