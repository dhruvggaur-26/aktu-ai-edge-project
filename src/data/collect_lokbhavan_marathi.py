import json
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from langdetect import detect, LangDetectException


BASE_URL = "https://lokbhavan.maharashtra.gov.in"

CATEGORY_PATH = (
    "/category/"
    "%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%B8%E0%A4%BF%E0%A4%A6%E0%A5%8D%E0%A4%A7%E0%A5%80%E0%A4%AA%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A4%95/"
)

OUTPUT_FILE = Path(
    "data/raw/lokbhavan_marathi_raw.jsonl"
)

TARGET_RECORDS = 350
MAX_PAGES = 24

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def normalize_text(text):
    """
    Normalize whitespace without changing the actual content.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def looks_like_marathi(text):
    """
    Basic Marathi sanity check.

    This is not a full language detector.
    It verifies that the page contains substantial
    Devanagari text and common Marathi words.
    """

    if not text:
        return False

    devanagari_count = len(
        re.findall(r"[\u0900-\u097F]", text)
    )

    marathi_markers = [
        "आहे",
        "आहेत",
        "यांनी",
        "यांना",
        "राज्यपाल",
        "महाराष्ट्र",
        "लोकभवन",
        "यावेळी",
        "कार्यक्रम",
        "शासन",
    ]

    marker_count = sum(
        marker in text
        for marker in marathi_markers
    )

    return (
        devanagari_count >= 100
        and marker_count >= 1
    )


def get_listing_url(page):
    """
    Build Lok Bhavan Marathi press-release listing URL.
    """

    if page == 1:
        return (
            BASE_URL
            + CATEGORY_PATH
            + "?cyear=2026"
        )

    return (
        BASE_URL
        + CATEGORY_PATH
        + f"page/{page}?cyear=2026"
    )


def get_candidate_urls():
    """
    Collect article URLs from paginated
    Lok Bhavan Marathi press-release listings.
    """

    candidate_urls = []
    seen_urls = set()

    print("\nCollecting article URLs...")

    for page in range(1, MAX_PAGES + 1):

        if len(candidate_urls) >= TARGET_RECORDS * 50:
            break

        listing_url = get_listing_url(page)

        print(
            f"\nFetching listing page {page}:"
        )
        print(listing_url)

        try:
            response = requests.get(
                listing_url,
                headers=HEADERS,
                timeout=30,
            )

            response.raise_for_status()

        except requests.RequestException as e:
            print(
                f"  -> Listing request failed: {e}"
            )
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        cards = soup.select(
            ".awardListing"
        )

        print(
            f"  -> Cards found: {len(cards)}"
        )

        if not cards:
            print(
                "  -> No cards found. "
                "Stopping pagination."
            )
            break

        new_urls = 0

        for card in cards:

            link = card.select_one(
                "a.arrowDetails"
            )

            if not link:
                continue

            href = link.get("href")

            if not href:
                continue

            article_url = urljoin(
                BASE_URL,
                href,
            )

            # Ignore non-HTML resources.
            if article_url.lower().endswith(
                (".pdf", ".doc", ".docx", ".xls", ".xlsx")
            ):
                continue

            if article_url in seen_urls:
                continue

            seen_urls.add(article_url)
            candidate_urls.append(article_url)
            new_urls += 1

        print(
            f"  -> New article URLs: {new_urls}"
        )

        print(
            f"  -> Total candidate URLs: "
            f"{len(candidate_urls)}"
        )

    return candidate_urls


def extract_article(url, record_number):
    """
    Fetch and extract one Lok Bhavan Marathi article.
    """

    print(
        f"\nFetching article {record_number}:"
    )
    print(url)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as e:
        print(
            f"  -> Article request failed: {e}"
        )
        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # -----------------------------
    # TITLE
    # -----------------------------

    title_tag = soup.select_one("h1")

    if not title_tag:
        print("  -> Title not found")
        return None

    title = normalize_text(
        title_tag.get_text(
            " ",
            strip=True,
        )
    )

    if not title:
        print("  -> Empty title")
        return None

    # -----------------------------
    # ARTICLE CONTENT
    # -----------------------------

    content_containers = soup.select(
        ".col-xs-12"
    )

    if len(content_containers) < 5:
        print(
            "  -> Expected article "
            "content container not found"
        )
        return None

    content_container = content_containers[4]

    paragraphs = content_container.select("p")

    text_parts = []

    for paragraph in paragraphs:

        paragraph_text = normalize_text(
            paragraph.get_text(
                " ",
                strip=True,
            )
        )

        if not paragraph_text:
            continue

        # -----------------------------
        # PARAGRAPH LANGUAGE DETECTION
        # -----------------------------

        try:
            detected_language = detect(
                paragraph_text
            )

        except LangDetectException:
            print(
                "  -> Language detection failed, "
                "skipping paragraph"
            )
            continue

        print(
            f"  -> Paragraph language: "
            f"{detected_language}"
        )

        # Keep only Marathi paragraphs.
        if detected_language != "mr":
            print(
                "  -> Skipping non-Marathi paragraph"
            )
            continue

        text_parts.append(
            paragraph_text
        )

    text = "\n".join(
        text_parts
    ).strip()

    print(
        f"  -> Extracted Marathi text length: "
        f"{len(text)}"
    )

    if not text:
        print(
            "  -> Empty article text"
        )
        return None

    # -----------------------------
    # MARATHI CHECK
    # -----------------------------

    combined_text = (
        title + " " + text
    )

    marathi_check = looks_like_marathi(
        combined_text
    )

    print(
        f"  -> Marathi check: "
        f"{marathi_check}"
    )

    if not marathi_check:
        print(
            "  -> Marathi language "
            "check failed"
        )
        return None

    # -----------------------------
    # PUBLISHED DATE
    # -----------------------------

    published_date = ""

    date_tag = soup.select_one(
        ".meta-info.odd"
    )

    if date_tag:

        published_date = normalize_text(
            date_tag.get_text(
                " ",
                strip=True,
            )
        )

    # -----------------------------
    # RECORD
    # -----------------------------

    record = {
        "id": f"LokBhavan_MR_{record_number:03d}",
        "source": "Lok Bhavan Maharashtra",
        "language": "mr",
        "category": "government_press_release",
        "title": title,
        "text": text,
        "source_url": url,
        "published_date": published_date,
        "date_collected": datetime.now().strftime(
            "%Y-%m-%d"
        ),
    }

    return record


def save_records(records):
    """
    Save records as UTF-8 JSONL.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main():

    print("=" * 40)
    print("LOK BHAVAN MARATHI COLLECTOR")
    print("=" * 40)

    print(
        f"Target records: {TARGET_RECORDS}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    candidate_urls = (
        get_candidate_urls()
    )

    print("\n" + "=" * 40)
    print(
        f"Candidate URLs found: "
        f"{len(candidate_urls)}"
    )
    print("=" * 40)

    records = []

    seen_urls = set()

    for url in candidate_urls:

        if len(records) >= TARGET_RECORDS:
            break

        if url in seen_urls:
            continue

        seen_urls.add(url)

        record = extract_article(
            url,
            len(records) + 1,
        )

        if record is None:
            continue

        records.append(record)

        print(
            f"  -> ACCEPTED: "
            f"{record['id']}"
        )

        print(
            f"     Title: "
            f"{record['title'][:100]}"
        )

    save_records(records)

    print("\n" + "=" * 40)
    print("COLLECTION COMPLETED")
    print("=" * 40)

    print(
        f"Records saved: {len(records)}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()