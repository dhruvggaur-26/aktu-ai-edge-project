import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.pmindia.gov.in"
LIST_URL = f"{BASE_URL}/en/news-updates/"
AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"

OUTPUT_FILE = Path("data/raw/pmindia_english_raw.jsonl")

TARGET_RECORDS = 100
MAX_AJAX_PAGES = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": LIST_URL,
}


def is_english_article_url(url):
    return (
        url.startswith(f"{BASE_URL}/en/news_updates/")
        and "/hi/" not in url
    )


def get_article_links(page_no):
    params = {
        "action": "infinite_scroll",
        "sort_type": "latest",
        "page_no": page_no,
        "query": "",
        "language": "en",
    }

    response = requests.get(
        AJAX_URL,
        params=params,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0].strip()

        if is_english_article_url(href):
            links.append(href)

    return list(dict.fromkeys(links))


def extract_article(url, record_id):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    content_block = soup.find("div", class_="content-block")

    if not content_block:
        print("  Skipping: content block not found")
        return None

    title_tag = content_block.find("h2")
    date_tag = content_block.find("div", class_="share_date")
    news_bg = content_block.find("div", class_="news-bg")

    if not title_tag or not news_bg:
        print("  Skipping: title/article body not found")
        return None

    title = title_tag.get_text(" ", strip=True)
    text = news_bg.get_text("\n", strip=True)

    if not title or not text:
        print("  Skipping: empty title/text")
        return None

    date = ""
    if date_tag:
        date = date_tag.get_text(" ", strip=True)

    return {
        "id": record_id,
        "source": "PM India",
        "language": "en",
        "category": "government",
        "title": title,
        "text": text,
        "date": date,
        "source_url": url,
    }


def main():
    records = []
    seen_urls = set()

    for page_no in range(1, MAX_AJAX_PAGES + 1):
        if len(records) >= TARGET_RECORDS:
            break

        print(f"\nAJAX PAGE {page_no}")

        try:
            links = get_article_links(page_no)
        except Exception as e:
            print(f"  Page failed: {e}")
            continue

        print(f"  Found {len(links)} unique links")

        for url in links:
            if len(records) >= TARGET_RECORDS:
                break

            if url in seen_urls:
                continue

            seen_urls.add(url)

            print(f"  Collecting: {url}")

            try:
                record_id = f"PMIndia_EN_{len(records) + 1:03d}"
                record = extract_article(url, record_id)

                if record:
                    records.append(record)
                    print(f"  Added: {record['title'][:80]}")

            except Exception as e:
                print(f"  Failed: {e}")

            time.sleep(0.5)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("\nCollection completed.")
    print(f"Total records: {len(records)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()