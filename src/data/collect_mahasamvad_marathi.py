import json
import re
import time
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException


BASE_URL = "https://www.mahasamvad.in"
START_URL = f"{BASE_URL}/page/843/"

OUTPUT_FILE = Path(
    "data/raw/mahasamvad_marathi_raw.jsonl"
)

TARGET_RECORDS = 150
MAX_PAGES = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def normalize_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def looks_like_marathi(text):

    devanagari = len(
        re.findall(r"[\u0900-\u097F]", text)
    )

    marathi_markers = [
        "आहे",
        "आहेत",
        "यांनी",
        "यांना",
        "महाराष्ट्र",
        "शासन",
        "सरकार",
        "राज्य",
        "जिल्हा",
        "विभाग",
        "यावेळी",
        "कार्यक्रम",
        "मंत्री",
        "मुख्यमंत्री",
    ]

    marker_count = sum(
        1
        for marker in marathi_markers
        if marker in text
    )

    return (
        devanagari >= 100
        and marker_count >= 1
    )


def get_page_url(page_number):

    if page_number == 1:
        return START_URL

    return (
        f"{BASE_URL}/page/"
        f"{843 + page_number - 1}/"
    )


def get_candidate_urls(session):

    urls = []
    seen = set()

    for page in range(
        1,
        MAX_PAGES + 1
    ):

        url = get_page_url(page)

        print(
            f"\nListing page {page}: {url}"
        )

        try:

            response = session.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            print(
                "Status:",
                response.status_code
            )

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for link in soup.find_all(
                "a",
                href=True
            ):

                href = link["href"].strip()

                if not href.startswith("http"):
                    continue

                if (
                    "mahasamvad.in"
                    not in href
                ):
                    continue

                # Remove URL fragments
                href = href.split("#")[0]

                # Remove trailing slash
                href = href.rstrip("/")

                # Convert back to standard format
                href = href + "/"

                # --------------------------------
                # ONLY NUMERIC ARTICLE URLS
                # Example:
                # https://www.mahasamvad.in/217057/
                # --------------------------------

                path = href.replace(
                    BASE_URL,
                    ""
                )

                if not re.fullmatch(
                    r"/\d+/",
                    path
                ):
                    continue

                if href in seen:
                    continue

                seen.add(href)
                urls.append(href)

        except requests.RequestException as e:

            print(
                "Listing error:",
                e
            )

        time.sleep(0.5)

    return urls


def extract_article(
    session,
    url
):

    try:

        response = session.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:

            print(
                "  -> HTTP",
                response.status_code
            )

            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # --------------------------------
        # TITLE
        # --------------------------------

        title_tag = soup.find("h1")

        if not title_tag:
            title_tag = soup.find("h2")

        if not title_tag:
            return None

        title = normalize_text(
            title_tag.get_text(
                " ",
                strip=True
            )
        )

        if not title:
            return None

        # --------------------------------
        # ARTICLE PARAGRAPHS
        # --------------------------------

        paragraphs = []

        marathi_markers = [
            "आहे",
            "आहेत",
            "यांनी",
            "यांना",
            "महाराष्ट्र",
            "शासन",
            "सरकार",
            "राज्य",
            "जिल्हा",
            "विभाग",
            "यावेळी",
            "कार्यक्रम",
            "मंत्री",
            "मुख्यमंत्री",
        ]

        for p in soup.find_all("p"):

            text = normalize_text(
                p.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            try:

                lang = detect(text)

            except LangDetectException:

                continue

            # Normal Marathi detection
            if lang == "mr":

                paragraphs.append(text)

            # langdetect sometimes incorrectly
            # detects short Marathi headings as Hindi.
            elif lang == "hi":

                if any(
                    marker in text
                    for marker in marathi_markers
                ):

                    paragraphs.append(text)

        if not paragraphs:

            return None

        text = "\n".join(
            paragraphs
        )

        # --------------------------------
        # Remove trailing source markers
        # --------------------------------

        text = re.sub(
            r"\n?००००\s*$",
            "",
            text
        ).strip()

        # --------------------------------
        # MARATHI QUALITY CHECK
        # --------------------------------

        if not looks_like_marathi(text):

            return None

        # --------------------------------
        # PUBLISHED DATE
        # --------------------------------

        published_date = ""

        page_text = soup.get_text(
            " ",
            strip=True
        )

        date_match = re.search(
            r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b",
            page_text
        )

        if date_match:

            published_date = (
                date_match.group(0)
            )

        return {
            "title": title,
            "text": text,
            "source_url": url,
            "published_date": published_date,
            "date_collected": (
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            ),
        }

    except requests.RequestException as e:

        print(
            "  -> Article error:",
            e
        )

        return None


def load_existing_records():

    records = []
    seen_urls = set()

    if not OUTPUT_FILE.exists():

        return (
            records,
            seen_urls
        )

    print(
        "\nLoading existing records..."
    )

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:

                record = json.loads(
                    line
                )

            except json.JSONDecodeError:

                print(
                    "Skipping invalid JSON line."
                )

                continue

            records.append(record)

            existing_url = (
                record.get(
                    "source_url",
                    ""
                )
                .split("#")[0]
                .rstrip("/")
                + "/"
            )

            if existing_url != "/":

                seen_urls.add(
                    existing_url
                )

    print(
        "Existing records loaded:",
        len(records)
    )

    return (
        records,
        seen_urls
    )


def save_records(records):

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


def main():

    print("=" * 60)
    print(
        "MAHASAMVAD MARATHI COLLECTOR"
    )
    print("=" * 60)

    session = requests.Session()

    # --------------------------------
    # LOAD EXISTING RECORDS
    # --------------------------------

    (
        records,
        seen_urls
    ) = load_existing_records()

    if len(records) >= TARGET_RECORDS:

        print(
            f"\nTarget already reached: "
            f"{len(records)} records."
        )

        return

    # --------------------------------
    # GET CANDIDATE URLs
    # --------------------------------

    candidate_urls = (
        get_candidate_urls(
            session
        )
    )

    print(
        "\nCandidate URLs found:",
        len(candidate_urls)
    )

    print(
        "\nFIRST 20 CANDIDATE URLs:"
    )

    for u in candidate_urls[:20]:

        print(u)

    # --------------------------------
    # COLLECT NEW RECORDS
    # --------------------------------

    for url in candidate_urls:

        if len(records) >= TARGET_RECORDS:

            break

        url = (
            url
            .split("#")[0]
            .rstrip("/")
            + "/"
        )

        # Skip already collected URLs
        if url in seen_urls:

            continue

        print(
            f"\n[{len(records) + 1}/"
            f"{TARGET_RECORDS}] "
            f"Checking: {url}"
        )

        article = extract_article(
            session,
            url
        )

        if article is None:

            print(
                "  -> Skipped"
            )

            continue

        record = {

            "id": (
                f"MahaSamvad_MR_"
                f"{len(records) + 1:03d}"
            ),

            "source":
                "MahaSamvad",

            "language":
                "mr",

            "category":
                "government_news",

            "title":
                article["title"],

            "text":
                article["text"],

            "source_url":
                article["source_url"],

            "published_date":
                article[
                    "published_date"
                ],

            "date_collected":
                article[
                    "date_collected"
                ],
        }

        records.append(record)

        seen_urls.add(url)

        print(
            "  -> Accepted"
        )

        print(
            "  -> Title:",
            record["title"]
        )

        print(
            "  -> Text length:",
            len(record["text"])
        )

        time.sleep(0.5)

    # --------------------------------
    # SAVE
    # --------------------------------

    save_records(records)

    print(
        "\n" + "=" * 60
    )

    print(
        "COLLECTION COMPLETED"
    )

    print(
        "=" * 60
    )

    print(
        "Records saved:",
        len(records)
    )

    print(
        "Output file:",
        OUTPUT_FILE
    )


if __name__ == "__main__":

    main()