import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.pib.gov.in"
LIST_URL = f"{BASE_URL}/AllRelease.aspx?lang=1&reg=48"

OUTPUT_FILE = Path("data/raw/pib_english_raw.jsonl")

TARGET_RECORDS = 100

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


def get_release_links():
    response = requests.get(
        LIST_URL,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if "/PressReleseDetail.aspx?PRID=" in href:
            full_url = urljoin(BASE_URL, href)

            if full_url not in links:
                links.append(full_url)

    return links


def extract_release(detail_url, record_id):
    response = requests.get(
        detail_url,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    iframe = soup.find(
        "iframe",
        id="ContentPlaceHolder1_iframepressrealese"
    )

    if not iframe or not iframe.get("src"):
        print("  Skipping: release iframe not found")
        return None

    iframe_url = urljoin(detail_url, iframe["src"])

    response = requests.get(
        iframe_url,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    release_soup = BeautifulSoup(response.text, "html.parser")

    title_tag = release_soup.find("h2", id="Titleh2")

    if not title_tag:
        print("  Skipping: title not found")
        return None

    title = title_tag.get_text(" ", strip=True)

    paragraphs = []

    for p in release_soup.find_all("p"):
        text = p.get_text(" ", strip=True)

        if not text:
            continue

        if text in {"***", "SR/SV/SG"}:
            continue

        paragraphs.append(text)

    text = "\n".join(paragraphs).strip()

    if not text:
        print("  Skipping: empty article text")
        return None

    return {
        "id": record_id,
        "source": "PIB",
        "language": "en",
        "category": "government",
        "title": title,
        "text": text,
        "source_url": iframe_url,
    }


def main():
    records = []
    seen_urls = set()

    print("Fetching PIB English release links...")

    links = get_release_links()

    print(f"Found {len(links)} release links")

    for detail_url in links:
        if len(records) >= TARGET_RECORDS:
            break

        if detail_url in seen_urls:
            continue

        seen_urls.add(detail_url)

        print(f"\nCollecting: {detail_url}")

        try:
            record_id = f"PIB_EN_{len(records) + 1:03d}"

            record = extract_release(
                detail_url,
                record_id,
            )

            if record:
                records.append(record)
                print(f"Added: {record['title'][:100]}")

        except Exception as e:
            print(f"Failed: {e}")

        time.sleep(0.5)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                ) + "\n"
            )

    print("\nCollection completed.")
    print(f"Total records: {len(records)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
