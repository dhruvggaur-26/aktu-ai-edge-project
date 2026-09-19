import json
import time
from pathlib import Path
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)


BASE_URL = "https://ddnews.gov.in"
START_URL = "https://ddnews.gov.in/category/national/"
OUTPUT_FILE = Path("data/raw/ddnews_hindi_raw.jsonl")

TARGET_RECORDS = 145
MAX_PAGES = 30
WAIT_SECONDS = 5


def load_existing_records():
    """Load existing DD News records."""
    records = []

    if not OUTPUT_FILE.exists():
        return records

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print("Warning: Invalid JSON line skipped.")

    return records


def save_record(record):
    """Append one record safely to JSONL."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


def get_next_id(existing_records):
    """Find next DD News ID."""

    max_id = 0

    for record in existing_records:

        record_id = record.get("ID", "")

        if record_id.startswith("DDNews_HI_"):

            try:
                number = int(
                    record_id.replace(
                        "DDNews_HI_",
                        ""
                    )
                )

                max_id = max(
                    max_id,
                    number
                )

            except ValueError:
                continue

    return max_id + 1


def get_listing_links(driver):
    """Get article links from current listing page."""

    links = driver.find_elements(
        By.CSS_SELECTOR,
        "h3.entry-title a"
    )

    urls = []

    for link in links:

        url = link.get_attribute("href")

        if not url:
            continue

        url = urljoin(
            BASE_URL,
            url
        )

        if url not in urls:
            urls.append(url)

    return urls


def extract_article(driver, url):
    """Open article using the same browser session."""

    try:

        driver.get(
            url
        )

        time.sleep(
            WAIT_SECONDS
        )

        title = driver.find_element(
            By.CSS_SELECTOR,
            "h2.mb-0.text-capitalize"
        ).text.strip()

        body = driver.find_element(
            By.CSS_SELECTOR,
            ".entry-content"
        )

        paragraphs = []

        for paragraph in body.find_elements(
            By.TAG_NAME,
            "p"
        ):

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        article_text = "\n".join(
            paragraphs
        ).strip()

        if not title:
            print(
                f"Skipped: empty title | {url}"
            )
            return None

        if not article_text:
            print(
                f"Skipped: empty text | {url}"
            )
            return None

        return {
            "Title": title,
            "Text": article_text,
            "Url": url
        }

    except (
        NoSuchElementException,
        TimeoutException,
        WebDriverException
    ) as error:

        print(
            f"Failed: {url}"
        )

        print(
            f"Reason: {error}"
        )

        return None


def main():

    print(
        "Starting DD News Hindi collector..."
    )

    print(
        f"Target total DD News records: "
        f"{TARGET_RECORDS}"
    )

    # ----------------------------------
    # Existing records
    # ----------------------------------

    existing_records = load_existing_records()

    existing_urls = {
        record.get("Url")
        for record in existing_records
        if record.get("Url")
    }

    current_count = len(existing_records)

    next_id = get_next_id(
        existing_records
    )

    print(
        f"Existing records: {current_count}"
    )

    print(
        f"Next ID: DDNews_HI_{next_id:03d}"
    )

    if current_count >= TARGET_RECORDS:

        print(
            "Target already reached."
        )

        return

    # ----------------------------------
    # Start ONE Chromium session
    # ----------------------------------

    options = Options()

    options.add_argument(
        "--start-maximized"
    )

    driver = webdriver.Chrome(
        options=options
    )

    try:

        page_number = 1

        while (
            current_count < TARGET_RECORDS
            and page_number <= MAX_PAGES
        ):

            if page_number == 1:

                listing_url = START_URL

            else:

                listing_url = (
                    f"{BASE_URL}"
                    f"/category/national/"
                    f"page/{page_number}/"
                )

            print(
                "\n--------------------------------"
            )

            print(
                f"Opening listing page {page_number}"
            )

            print(
                listing_url
            )

            try:

                driver.get(
                    listing_url
                )

                time.sleep(
                    WAIT_SECONDS
                )

            except WebDriverException as error:

                print(
                    "Listing page failed:"
                )

                print(error)

                page_number += 1

                continue

            article_urls = get_listing_links(
                driver
            )

            print(
                f"Article links found: "
                f"{len(article_urls)}"
            )

            if not article_urls:

                print(
                    "No article links found."
                )

                page_number += 1

                continue

            new_links = [
                url
                for url in article_urls
                if url not in existing_urls
            ]

            print(
                f"New article links: "
                f"{len(new_links)}"
            )

            for url in new_links:

                if current_count >= TARGET_RECORDS:
                    break

                print(
                    "\nCollecting:"
                )

                print(url)

                article = extract_article(
                    driver,
                    url
                )

                if not article:
                    continue

                record = {
                    "ID": (
                        f"DDNews_HI_"
                        f"{next_id:03d}"
                    ),
                    "Title": article["Title"],
                    "Text": article["Text"],
                    "Source": "DD News",
                    "Url": article["Url"],
                    "Language": "hi",
                    "Category": "news",
                    "Department": "",
                    "Date_collected": time.strftime(
                        "%Y-%m-%d"
                    )
                }

                save_record(
                    record
                )

                existing_urls.add(
                    url
                )

                current_count += 1
                next_id += 1

                print(
                    f"Collected: "
                    f"{record['ID']}"
                )

                print(
                    f"Total: "
                    f"{current_count}/{TARGET_RECORDS}"
                )

                # Small delay
                time.sleep(1)

            page_number += 1

        print(
            "\n================================"
        )

        print(
            "Collection complete."
        )

        print(
            f"Total DD News records: "
            f"{current_count}"
        )

        print(
            f"Target: {TARGET_RECORDS}"
        )

        print(
            f"Output: {OUTPUT_FILE}"
        )

    finally:

        driver.quit()

        print(
            "\nChromium session closed."
        )


if __name__ == "__main__":
    main()