import json
import requests

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


BASE_URL = "https://www.newsonair.gov.in"

LISTING_URL = (
    "https://www.newsonair.gov.in/"
    "hi/category/national/page/{}/"
)

OUTPUT_FILE = (
    "data/raw/newsonair_hindi_raw.jsonl"
)

TARGET_RECORDS = 100
MAX_PAGES = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_article_urls(page_number):
    """Collect article URLs from a Hindi National News On AIR page."""

    url = LISTING_URL.format(page_number)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    urls = []

    for article in soup.find_all("article"):

        link = article.find(
            "a",
            href=True
        )

        if not link:
            continue

        article_url = urljoin(
            BASE_URL,
            link["href"]
        )

        if "/hi/" in article_url:
            urls.append(article_url)

    return list(
        dict.fromkeys(urls)
    )


def extract_article(url):
    """Extract title, date and text from one News On AIR article."""

    response = None

    # Retry article request up to 3 times
    for attempt in range(3):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=60
            )

            break

        except requests.RequestException as error:

            print(
                f"Attempt {attempt + 1}/3 failed: "
                f"{url} | {error}"
            )

    if response is None:

        print(
            f"Failed: {url} | "
            "All 3 attempts failed"
        )

        return None

    if response.status_code != 200:

        print(
            f"Failed: {url} | "
            f"Status code: {response.status_code}"
        )

        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Article container
    article = soup.find("article")

    if not article:

        print(
            f"Failed: {url} | "
            "Article container not found"
        )

        return None

    # Title
    title_tag = article.select_one(
        "h2.mb-0.text-capitalize"
    )

    if not title_tag:

        print(
            f"Failed: {url} | "
            "Title not found"
        )

        return None

    title = title_tag.get_text(
        " ",
        strip=True
    )

    # Date
    title_row = article.select_one(
        "div.titleRow"
    )

    date_text = ""

    if title_row:

        date_parts = list(
            title_row.stripped_strings
        )

        if len(date_parts) >= 2:

            date_text = date_parts[1]

    # Hindi month mapping
    hindi_months = {

        "जनवरी": "01",
        "फरवरी": "02",
        "मार्च": "03",
        "अप्रैल": "04",
        "मई": "05",
        "जून": "06",
        "जुलाई": "07",
        "अगस्त": "08",

        "सितम्बर": "09",
        "सितंबर": "09",

        "अक्टूबर": "10",
        "नवंबर": "11",

        "दिसम्बर": "12",
        "दिसंबर": "12"
    }

    # Convert Hindi date to YYYY-MM-DD
    for month, month_number in hindi_months.items():

        if month in date_text:

            parts = date_text.split(",")

            if len(parts) >= 2:

                day_parts = (
                    parts[0]
                    .strip()
                    .split()
                )

                year_parts = (
                    parts[1]
                    .strip()
                    .split()
                )

                if len(day_parts) >= 2 and year_parts:

                    day = day_parts[1]
                    year = year_parts[0]

                    try:

                        date_text = (
                            f"{year}-"
                            f"{month_number}-"
                            f"{int(day):02d}"
                        )

                    except ValueError:

                        pass

            break

    # Article body
    body = article.select_one(
        "div.post-inner.thin"
    )

    if not body:

        print(
            f"Failed: {url} | "
            "Article body not found"
        )

        return None

    paragraphs = body.find_all("p")

    text_parts = []

    for paragraph in paragraphs:

        text = paragraph.get_text(
            " ",
            strip=True
        )

        if text:

            text_parts.append(text)

    text = "\n".join(
        text_parts
    )

    if not text:

        print(
            f"Failed: {url} | "
            "Article text is empty"
        )

        return None

    return {

        "Title": title,

        "Text": text,

        "Date": date_text,

        "Url": url
    }


def main():

    print(
        "Starting News On AIR "
        "Hindi collection...\n"
    )

    records = []

    seen_urls = set()

    for page in range(
        1,
        MAX_PAGES + 1
    ):

        if len(records) >= TARGET_RECORDS:

            break

        print(
            f"Checking page {page}..."
        )

        try:

            urls = get_article_urls(
                page
            )

        except Exception as error:

            print(
                f"Page {page} failed: "
                f"{error}"
            )

            continue

        print(
            f"Found {len(urls)} "
            "article URLs"
        )

        for url in urls:

            if len(records) >= TARGET_RECORDS:

                break

            if url in seen_urls:

                continue

            seen_urls.add(url)

            try:

                article = extract_article(
                    url
                )

            except Exception as error:

                print(
                    f"Failed: {url} | "
                    f"{error}"
                )

                continue

            if not article:

                continue

            record_id = (
                f"NewsOnAir_HI_"
                f"{len(records) + 1:03d}"
            )

            record = {

                "ID": record_id,

                "Title": article["Title"],

                "Text": article["Text"],

                "Source": "News On AIR",

                "Url": article["Url"],

                "Language": "hi",

                "Category": "news",

                "Department": "",

                "Date_collected": article["Date"]
            }

            records.append(
                record
            )

            print(
                f"Collected "
                f"{len(records)}: "
                f"{record['Title'][:70]}"
            )

    # Create output directory if needed
    Path(
        OUTPUT_FILE
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save JSONL
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

    print(
        "\nCollection complete."
    )

    print(
        f"Records collected: "
        f"{len(records)}"
    )

    print(
        f"Output file: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":

    main()