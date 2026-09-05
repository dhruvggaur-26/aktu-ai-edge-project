from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from html import unescape
from pathlib import Path
from datetime import date
import json


BASE_URL = "https://www.pib.gov.in"
LIST_URL = "https://www.pib.gov.in/allRel.aspx?reg=48&lang=2"

OUTPUT_FILE = "data/raw/pib_raw.jsonl"


def build_release_url(href):
    """
    Convert relative PIB links into absolute URLs.
    """

    if href.startswith("http://") or href.startswith("https://"):
        return href

    if href.startswith("/"):
        return BASE_URL + href

    return BASE_URL + "/" + href.lstrip("/")


def extract_release(context, release_url):
    """
    Extract title, department and text from one PIB release.
    """

    detail_page = context.new_page()

    try:
        print("Opening release page...")

        detail_page.goto(
            release_url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        detail_page.wait_for_timeout(1500)

        # PIB release pages contain the actual content inside an iframe.
        iframe = detail_page.locator("iframe").first

        if iframe.count() == 0:
            raise ValueError("Release iframe not found")

        iframe_src = iframe.get_attribute("src")

        if not iframe_src:
            raise ValueError("Iframe URL not found")

        iframe_url = build_release_url(iframe_src)

        print("Iframe URL:", iframe_url)

        iframe_page = context.new_page()

        try:
            iframe_page.goto(
                iframe_url,
                timeout=60000,
                wait_until="domcontentloaded"
            )

            iframe_page.wait_for_timeout(1000)

            # Title
            title_element = iframe_page.locator(
                "#ltrTitlee"
            )

            # Release description
            description_element = iframe_page.locator(
                "#ltrDescriptionn"
            )

            # Ministry / Department
            ministry_element = iframe_page.locator(
                "#MinistryName"
            )

            title = ""

            if title_element.count() > 0:
                title = (
                    title_element
                    .get_attribute("value")
                    or ""
                )

            description_html = ""

            if description_element.count() > 0:
                description_html = (
                    description_element
                    .get_attribute("value")
                    or ""
                )

            ministry = ""

            if ministry_element.count() > 0:
                ministry = ministry_element.inner_text()

            # Decode HTML entities
            description_html = unescape(
                description_html
            )

            # Convert HTML description to plain text
            text = BeautifulSoup(
                description_html,
                "html.parser"
            ).get_text(
                " ",
                strip=True
            )

            # Extract PRID from URL
            release_id = (
                release_url
                .split("PRID=")[-1]
                .split("&")[0]
            )

            record = {
                "ID": release_id,
                "Title": title.strip(),
                "Text": text,
                "Source": "PIB",
                "Url": release_url,
                "Language": "hi",
                "Category": "Press Release",
                "Department": ministry.strip(),
                "Date_collected": str(date.today()),
            }

            return record

        finally:
            iframe_page.close()

    finally:
        detail_page.close()


def collect_releases():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        try:

            # -----------------------------------------
            # STEP 1: Open PIB release listing page
            # -----------------------------------------

            print("Opening PIB release page...")

            page.goto(
                LIST_URL,
                timeout=60000,
                wait_until="domcontentloaded"
            )

            page.wait_for_timeout(3000)

            # -----------------------------------------
            # STEP 2: Trigger date selection/postback
            # -----------------------------------------

            print("Triggering PIB date postback...")

            page.select_option(
                "#ContentPlaceHolder1_ddlday",
                "1"
            )

            page.wait_for_timeout(5000)

            # -----------------------------------------
            # STEP 3: Collect release links
            # -----------------------------------------

            links = page.locator(
                'a[href*="PressReleaseDetail.aspx"], '
                'a[href*="PressReleasePage.aspx"]'
            )

            print(
                "Release links found:",
                links.count()
            )

            release_urls = []

            for link in links.all():

                href = link.get_attribute("href")

                if not href:
                    continue

                release_url = build_release_url(
                    href
                )

                if release_url not in release_urls:
                    release_urls.append(
                        release_url
                    )

            print(
                "Unique release URLs:",
                len(release_urls)
            )

            # -----------------------------------------
            # STEP 4: Create output directory
            # -----------------------------------------

            Path("data/raw").mkdir(
                parents=True,
                exist_ok=True
            )

            records = []

            # -----------------------------------------
            # STEP 5: Extract every release
            # -----------------------------------------

            for index, release_url in enumerate(
                release_urls,
                start=1
            ):

                print(
                    f"\n[{index}/{len(release_urls)}]"
                )

                print(
                    "URL:",
                    release_url
                )

                try:

                    record = extract_release(
                        context,
                        release_url
                    )

                    # Basic validation
                    if not record["Title"]:
                        raise ValueError(
                            "Title not extracted"
                        )

                    if not record["Text"]:
                        raise ValueError(
                            "Text not extracted"
                        )

                    records.append(record)

                    print(
                        "Collected:",
                        record["Title"][:100]
                    )

                    print(
                        "Department:",
                        record["Department"]
                    )

                    print(
                        "Text length:",
                        len(record["Text"])
                    )

                except Exception as error:

                    print(
                        "FAILED:",
                        error
                    )

            # -----------------------------------------
            # STEP 6: Save raw dataset
            # -----------------------------------------

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
                        ) + "\n"
                    )

            # -----------------------------------------
            # STEP 7: Final summary
            # -----------------------------------------

            print("\n--------------------------------")

            print(
                "Raw PIB dataset saved to:",
                OUTPUT_FILE
            )

            print(
                "Total records collected:",
                len(records)
            )

            print(
                "Failed records:",
                len(release_urls) - len(records)
            )

        finally:

            context.close()
            browser.close()


if __name__ == "__main__":
    collect_releases()