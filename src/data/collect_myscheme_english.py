import json
import re
import time
from pathlib import Path

import requests


SEARCH_API = "https://www.myscheme.gov.in/api/apisetu/search/schemes"
SCHEME_API = "https://www.myscheme.gov.in/api/apisetu/schemes"

TARGET_RECORDS = 100
PAGE_SIZE = 10

OUTPUT_FILE = Path("data/raw/myscheme_english_raw.jsonl")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def clean_text(text):
    if not text:
        return ""

    text = str(text)

    # Convert common HTML line breaks into spaces/newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Fix common UTF-8 mojibake
    try:
        fixed = text.encode("cp1252").decode("utf-8")
        if fixed != text:
            text = fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Normalize whitespace while preserving paragraphs
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text(value):
    """
    Recursively extract useful textual content from MyScheme
    nested API structures.
    """

    parts = []

    if value is None:
        return parts

    if isinstance(value, str):
        cleaned = clean_text(value)

        if cleaned:
            parts.append(cleaned)

    elif isinstance(value, list):
        for item in value:
            parts.extend(extract_text(item))

    elif isinstance(value, dict):

        # Prefer actual text fields
        if "text" in value:
            parts.extend(extract_text(value["text"]))

        elif "children" in value:
            parts.extend(extract_text(value["children"]))

        elif "process" in value:
            parts.extend(extract_text(value["process"]))

        elif "description" in value:
            parts.extend(extract_text(value["description"]))

        elif "content" in value:
            parts.extend(extract_text(value["content"]))

    return parts


def fetch_json(url, params=None, retries=3):
    for attempt in range(1, retries + 1):

        try:
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=60,
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:

            print(
                f"Request failed "
                f"(attempt {attempt}/{retries}): {e}"
            )

            if attempt < retries:
                time.sleep(2)

    return None


def get_scheme_slugs():
    """
    Collect unique Central scheme slugs from MyScheme search API.
    """

    slugs = []
    seen = set()

    offset = 0

    while len(slugs) < TARGET_RECORDS:

        print(f"\nFetching scheme list: from={offset}")

        params = {
            "lang": "en",
            "q": "[]",
            "keyword": "",
            "sort": "",
            "from": offset,
            "size": PAGE_SIZE,
        }

        data = fetch_json(SEARCH_API, params=params)

        if not data:
            print("Could not fetch scheme list.")
            break

        items = data.get("data", {}).get("hits", {}).get("items", [])

        if not items:
            print("No more schemes returned.")
            break

        for item in items:

            fields = item.get("fields", {})
            slug = fields.get("slug")

            if not slug:
                continue

            if slug in seen:
                continue

            seen.add(slug)
            slugs.append(slug)

            print(
                f"  {len(slugs):03d}. "
                f"{item.get('schemeName', 'Unknown')} "
                f"-> {slug}"
            )

            if len(slugs) >= TARGET_RECORDS:
                break

        offset += PAGE_SIZE

        time.sleep(0.5)

    return slugs


def build_text(en_data):
    """
    Build one clean text field from important MyScheme sections.
    """

    sections = []

    scheme_content = en_data.get("schemeContent", {})
    eligibility = en_data.get("eligibilityCriteria", {})
    application = en_data.get("applicationProcess", [])

    # Brief Description
    brief = scheme_content.get("briefDescription")

    if brief:
        text = clean_text(brief)

        if text:
            sections.append(
                "Brief Description:\n" + text
            )

    # Detailed Description
    detailed = scheme_content.get("detailedDescription")

    detailed_parts = extract_text(detailed)

    if detailed_parts:
        sections.append(
            "Detailed Description:\n"
            + "\n".join(detailed_parts)
        )

    # Eligibility
    eligibility_text = eligibility.get(
        "eligibilityDescription"
    )

    eligibility_parts = extract_text(eligibility_text)

    if eligibility_parts:
        sections.append(
            "Eligibility:\n"
            + "\n".join(eligibility_parts)
        )

    # Benefits
    benefits = scheme_content.get("benefits")

    benefits_parts = extract_text(benefits)

    if benefits_parts:
        sections.append(
            "Benefits:\n"
            + "\n".join(benefits_parts)
        )

    # Application Process
    application_parts = extract_text(application)

    if application_parts:
        sections.append(
            "Application Process:\n"
            + "\n".join(application_parts)
        )

    return "\n\n".join(sections).strip()


def build_record(index, data):
    en_data = data.get("en", {})

    basic = en_data.get("basicDetails", {})
    scheme_content = en_data.get("schemeContent", {})
    eligibility = en_data.get("eligibilityCriteria", {})

    slug = data.get("slug", "")

    title = basic.get("schemeName", "")

    text = build_text(en_data)

    record = {
        "id": f"MYSCHEME_EN_{index:03d}",
        "source": "MyScheme",
        "language": "en",
        "category": "government_scheme",
        "title": clean_text(title),
        "text": text,
        "source_url": f"https://www.myscheme.gov.in/schemes/{slug}",

        # MyScheme-specific metadata
        "scheme_short_title": clean_text(
            basic.get("schemeShortTitle", "")
        ),

        "level": basic.get("level", ""),

        "nodal_ministry": clean_text(
            basic.get("nodalMinistryName", "")
        ),

        "nodal_department": clean_text(
            basic.get("nodalDepartmentName", "")
        ),

        "scheme_type": clean_text(
            basic.get("schemeType", "")
        ),

        "scheme_for": clean_text(
            basic.get("schemeFor", "")
        ),

        "scheme_category": basic.get(
            "schemeCategory", []
        ),

        "target_beneficiaries": basic.get(
            "targetBeneficiaries", []
        ),

        "tags": basic.get(
            "tags", []
        ),

        "benefit_type": basic.get(
            "benefitTypes",
            scheme_content.get("benefitTypes", "")
        ),

        "slug": slug,
    }

    return record


def main():

    print("=" * 60)
    print("MyScheme English Data Collection")
    print("=" * 60)

    print("\nStep 1: Collecting scheme slugs...")

    slugs = get_scheme_slugs()

    print(
        f"\nUnique slugs collected: {len(slugs)}"
    )

    if len(slugs) < TARGET_RECORDS:
        print(
            "WARNING: Could not collect "
            f"{TARGET_RECORDS} unique schemes."
        )

    records = []

    print("\nStep 2: Fetching individual scheme data...")

    for index, slug in enumerate(
        slugs[:TARGET_RECORDS],
        start=1
    ):

        print(
            f"\n[{index}/{TARGET_RECORDS}] "
            f"Fetching: {slug}"
        )

        params = {
            "slug": slug,
            "lang": "en",
        }

        response = fetch_json(
            SCHEME_API,
            params=params
        )

        if not response:
            print("  FAILED: API response unavailable.")
            continue

        data = response.get("data")

        if not data:
            print("  FAILED: No data field.")
            continue

        record = build_record(
            len(records) + 1,
            data
        )

        # Basic quality checks
        if not record["title"]:
            print("  SKIPPED: Empty title.")
            continue

        if not record["text"]:
            print("  SKIPPED: Empty text.")
            continue

        if record["language"] != "en":
            print("  SKIPPED: Language is not English.")
            continue

        records.append(record)

        print(
            f"  Saved: {record['title']}"
        )
        print(
            f"  Text length: {len(record['text'])}"
        )

        time.sleep(0.5)

    # Save JSONL
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

    print("\n" + "=" * 60)
    print("COLLECTION COMPLETED")
    print("=" * 60)

    print(
        f"Records saved: {len(records)}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()