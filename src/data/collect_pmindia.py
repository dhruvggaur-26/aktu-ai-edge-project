import json
import time
from datetime import date
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


SEARCH_BASE_URL = "https://www.pmindia.gov.in/hi/"
OUTPUT_FILE = "data/raw/pmindia_hindi_raw.jsonl"

TARGET_RECORDS = 100
MAX_PAGES_PER_KEYWORD = 20

KEYWORDS = [
    "प्रधानमंत्री",
    "सरकार",
    "भारत",
    "विकास",
    "योजना",
    "किसान",
    "शिक्षा",
    "स्वास्थ्य",
    "रोजगार",
    "अर्थव्यवस्था",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load_existing_records():
    records = []

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    records.append(json.loads(line))
    except FileNotFoundError:
        pass

    return records


def get_search_urls(keyword, page):
    encoded_keyword = quote(keyword)

    if page == 1:
        return f"{SEARCH_BASE_URL}?s={encoded_keyword}"

    return f"{SEARCH_BASE_URL}page/{page}/?s={encoded_keyword}"


def get_news_urls(search_url):
    response = requests.get(
        search_url,
        headers=HEADERS,
        timeout=20
    )

    if response.status_code != 200:
        print(f"Search failed: {response.status_code}")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")

    urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/hi/news_updates/" in href:
            urls.add(href)

    return urls


def extract_article(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        article = soup.select_one("#printable .news-bg")
        title_tag = soup.select_one("#printable h2")
        date_tag = soup.select_one("#printable .share_date")

        if article is None or title_tag is None:
            return None

        paragraphs = article.find_all("p")

        text = " ".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if p.get_text(" ", strip=True)
        ).strip()

        title = title_tag.get_text(" ", strip=True)

        if not title or not text:
            return None

        article_date = ""

        if date_tag:
            article_date = date_tag.get_text(" ", strip=True)

        record = {
            "ID": "",
            "Title": title,
            "Text": text,
            "Source": "PM India",
            "Url": url,
            "Language": "hi",
            "Category": "news",
            "Department": "",
            "Date_collected": str(date.today())
        }

        return record

    except requests.RequestException:
        return None


def main():

    print("=" * 60)
    print("PM INDIA HINDI DATA COLLECTION")
    print("=" * 60)

    existing_records = load_existing_records()

    print(f"Existing records: {len(existing_records)}")

    existing_urls = {
        record.get("Url")
        for record in existing_records
        if record.get("Url")
    }

    all_urls = set(existing_urls)

    print("\nDiscovering article URLs...\n")

    for keyword in KEYWORDS:

        print(f"Keyword: {keyword}")

        for page in range(1, MAX_PAGES_PER_KEYWORD + 1):

            search_url = get_search_urls(keyword, page)

            page_urls = get_news_urls(search_url)

            print(f"  Page {page}: {len(page_urls)} URLs")

            new_urls = page_urls - all_urls

            all_urls.update(new_urls)

            if len(all_urls) >= TARGET_RECORDS:
                break

            if not page_urls:
                break

            time.sleep(0.5)

        if len(all_urls) >= TARGET_RECORDS:
            break

    print("\n" + "=" * 60)
    print(f"Unique URLs available: {len(all_urls)}")
    print("=" * 60)

    print("\nExtracting articles...\n")

    records = list(existing_records)

    next_id = len(records) + 1

    urls_to_process = [
        url for url in all_urls
        if url not in existing_urls
    ]

    for url in urls_to_process:

        if len(records) >= TARGET_RECORDS:
            break

        print(f"Checking: {url}")

        record = extract_article(url)

        if record is None:
            print("Skipped")
            continue

        record["ID"] = f"PMIndia_HI_{next_id:03d}"

        records.append(record)

        next_id += 1

        print(f"Collected: {record['ID']}")

        time.sleep(0.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Records collected: {len(records)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()