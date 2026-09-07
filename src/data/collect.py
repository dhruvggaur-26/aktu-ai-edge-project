import requests
from bs4 import BeautifulSoup
from html import unescape
from pathlib import Path
from datetime import date
from urllib.parse import urljoin
import json


BASE_URL = "https://www.pib.gov.in"
LIST_URL = "https://www.pib.gov.in/allRel.aspx?reg=48&lang=2"

OUTPUT_FILE = "data/raw/pib_raw.jsonl"


def build_release_url(href):
    """
    Convert relative PIB links into absolute URLs.
    """

    return urljoin(
        BASE_URL,
        href
    )


def get_hidden_fields(soup):
    """
    Extract ASP.NET hidden form fields.
    """

    data = {}

    for element in soup.select(
        'input[type="hidden"]'
    ):

        name = element.get("name")

        if name:

            data[name] = element.get(
                "value",
                ""
            )

    return data


def load_existing_ids():
    """
    Load IDs already present in the raw PIB dataset.
    """

    existing_ids = set()

    output_path = Path(OUTPUT_FILE)

    if not output_path.exists():
        return existing_ids

    with open(
        output_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:

                record = json.loads(line)

                record_id = record.get("ID")

                if record_id:

                    existing_ids.add(
                        str(record_id)
                    )

            except json.JSONDecodeError:

                print(
                    "WARNING: Invalid JSON line skipped."
                )

    return existing_ids


def extract_release(session, release_url, headers):
    """
    Extract title, department and text
    from one PIB release using requests.
    """

    # -----------------------------------------
    # Release page
    # -----------------------------------------

    response = session.get(
        release_url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # -----------------------------------------
    # Find iframe
    # -----------------------------------------

    iframe = soup.find("iframe")

    if not iframe:

        raise ValueError(
            "Release iframe not found"
        )

    iframe_src = iframe.get("src")

    if not iframe_src:

        raise ValueError(
            "Iframe URL not found"
        )

    iframe_url = build_release_url(
        iframe_src
    )

    # -----------------------------------------
    # Request iframe
    # -----------------------------------------

    iframe_response = session.get(
        iframe_url,
        headers=headers,
        timeout=30
    )

    iframe_response.raise_for_status()

    iframe_soup = BeautifulSoup(
        iframe_response.text,
        "html.parser"
    )

    # -----------------------------------------
    # Title
    # -----------------------------------------

    title_element = iframe_soup.select_one(
        "#ltrTitlee"
    )

    title = ""

    if title_element:

        title = (
            title_element.get("value")
            or title_element.get_text(
                strip=True
            )
        )

    # -----------------------------------------
    # Description
    # -----------------------------------------

    description_element = (
        iframe_soup.select_one(
            "#ltrDescriptionn"
        )
    )

    description_html = ""

    if description_element:

        description_html = (
            description_element.get(
                "value"
            )
            or ""
        )

    # -----------------------------------------
    # Ministry
    # -----------------------------------------

    ministry_element = (
        iframe_soup.select_one(
            "#MinistryName"
        )
    )

    ministry = ""

    if ministry_element:

        ministry = ministry_element.get_text(
            " ",
            strip=True
        )

    # -----------------------------------------
    # Convert HTML description to text
    # -----------------------------------------

    description_html = unescape(
        description_html
    )

    text = BeautifulSoup(
        description_html,
        "html.parser"
    ).get_text(
        " ",
        strip=True
    )

    # -----------------------------------------
    # Extract PRID
    # -----------------------------------------

    release_id = (
        release_url
        .split("PRID=")[-1]
        .split("&")[0]
    )

    # -----------------------------------------
    # Create record
    # -----------------------------------------

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


def collect_releases(day="1", month=None, year=None):
    """
    Collect Hindi PIB releases for the
    selected day, month and year.

    Existing records are preserved.
    Records with duplicate IDs are skipped.
    """

    # -----------------------------------------
    # Set default month and year
    # -----------------------------------------

    if month is None:

        month = date.today().month

    if year is None:

        year = date.today().year

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # -----------------------------------------
    # STEP 1: Initial GET
    # -----------------------------------------

    print(
        "Opening PIB release page..."
    )

    response = session.get(
        LIST_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # -----------------------------------------
    # STEP 2: Extract ASP.NET fields
    # -----------------------------------------

    data = get_hidden_fields(
        soup
    )

    # -----------------------------------------
    # STEP 3: Trigger date postback
    # -----------------------------------------

    print(
        "Triggering PIB date postback..."
    )

    print(
        f"Selected date: {day}-{month}-{year}"
    )

    data.update({

        "ctl00$ContentPlaceHolder1$ddlday":
            str(day),

        "ctl00$ContentPlaceHolder1$ddlMonth":
            str(month),

        "ctl00$ContentPlaceHolder1$ddlYear":
            str(year),

        "__EVENTTARGET":
            "ctl00$ContentPlaceHolder1$ddlday",

        "__EVENTARGUMENT":
            "",
    })

    post_response = session.post(
        LIST_URL,
        data=data,
        headers={
            **headers,
            "Referer": LIST_URL,
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        timeout=30
    )

    post_response.raise_for_status()

    post_soup = BeautifulSoup(
        post_response.text,
        "html.parser"
    )

    # -----------------------------------------
    # STEP 4: Collect release URLs
    # -----------------------------------------

    links = post_soup.select(
        'a[href*="PressReleaseDetail.aspx"], '
        'a[href*="PressReleasePage.aspx"]'
    )

    release_urls = []

    for link in links:

        href = link.get("href")

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
        "Release links found:",
        len(release_urls)
    )

    # -----------------------------------------
    # STEP 5: Create output directory
    # -----------------------------------------

    Path("data/raw").mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------
    # STEP 6: Load existing IDs
    # -----------------------------------------

    existing_ids = load_existing_ids()

    print(
        "Existing records found:",
        len(existing_ids)
    )

    records = []

    skipped_records = 0

    # -----------------------------------------
    # STEP 7: Extract releases
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
                session,
                release_url,
                headers
            )

            # ---------------------------------
            # Duplicate ID check
            # ---------------------------------

            if record["ID"] in existing_ids:

                print(
                    "SKIPPED: Record already exists:",
                    record["ID"]
                )

                skipped_records += 1

                continue

            # ---------------------------------
            # Basic validation
            # ---------------------------------

            if not record["Title"]:

                raise ValueError(
                    "Title not extracted"
                )

            if not record["Text"]:

                raise ValueError(
                    "Text not extracted"
                )

            records.append(
                record
            )

            # Add new ID immediately
            # to protect against duplicates
            # within the same collection.

            existing_ids.add(
                record["ID"]
            )

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
    # STEP 8: Append only new records
    # -----------------------------------------

    with open(
        OUTPUT_FILE,
        "a",
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
    # STEP 9: Final summary
    # -----------------------------------------

    print(
        "\n--------------------------------"
    )

    print(
        "Raw PIB dataset updated:",
        OUTPUT_FILE
    )

    print(
        "New records added:",
        len(records)
    )

    print(
        "Duplicate records skipped:",
        skipped_records
    )

    print(
        "Failed records:",
        len(release_urls)
        - len(records)
        - skipped_records
    )

    print(
        "Total records now in dataset:",
        len(load_existing_ids())
    )


def collect_date_range(
    start_day,
    end_day,
    month,
    year
):
    """
    Collect PIB releases for every day
    between start_day and end_day.
    """

    print(
        "\n================================"
    )

    print(
        "PIB DATE RANGE COLLECTION"
    )

    print(
        "================================"
    )

    print(
        f"Date range: "
        f"{start_day}-{month}-{year}"
        f" to "
        f"{end_day}-{month}-{year}"
    )

    for day in range(
        int(start_day),
        int(end_day) + 1
    ):

        print(
            "\n================================"
        )

        print(
            f"Processing date: "
            f"{day}-{month}-{year}"
        )

        print(
            "================================"
        )

        collect_releases(
            day=str(day),
            month=str(month),
            year=str(year)
        )


if __name__ == "__main__":

    collect_date_range(
        start_day=1,
        end_day=2,
        month=9,
        year=2026
    )