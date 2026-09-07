import requests
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import urljoin


BASE_URL = "https://www.pib.gov.in"
LIST_URL = "https://www.pib.gov.in/allRel.aspx?reg=48&lang=2"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}


# -----------------------------------------
# STEP 1: Initial GET
# -----------------------------------------

response = session.get(
    LIST_URL,
    headers=headers,
    timeout=30
)

print("Initial status:", response.status_code)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)


# -----------------------------------------
# STEP 2: ASP.NET hidden fields
# -----------------------------------------

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


# -----------------------------------------
# STEP 3: Trigger date postback
# -----------------------------------------

data.update({
    "ctl00$ContentPlaceHolder1$ddlday": "1",
    "ctl00$ContentPlaceHolder1$ddlMonth": "9",
    "ctl00$ContentPlaceHolder1$ddlYear": "2026",

    "__EVENTTARGET":
        "ctl00$ContentPlaceHolder1$ddlday",

    "__EVENTARGUMENT": ""
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

print(
    "POST status:",
    post_response.status_code
)


# -----------------------------------------
# STEP 4: Extract release URLs
# -----------------------------------------

post_soup = BeautifulSoup(
    post_response.text,
    "html.parser"
)

links = post_soup.select(
    'a[href*="PressReleaseDetail.aspx"], '
    'a[href*="PressReleasePage.aspx"]'
)

release_urls = []

for link in links:

    href = link.get("href")

    if not href:
        continue

    release_url = urljoin(
        BASE_URL,
        href
    )

    if release_url not in release_urls:

        release_urls.append(
            release_url
        )


print(
    "Release URLs found:",
    len(release_urls)
)


# -----------------------------------------
# STEP 5: Extract every release
# -----------------------------------------

successful = 0
failed = 0

for index, release_url in enumerate(
    release_urls,
    start=1
):

    print(
        f"\n[{index}/{len(release_urls)}]",
        release_url
    )

    try:

        # Request release page
        release_response = session.get(
            release_url,
            headers=headers,
            timeout=30
        )

        if release_response.status_code != 200:

            raise ValueError(
                f"Release status "
                f"{release_response.status_code}"
            )

        release_soup = BeautifulSoup(
            release_response.text,
            "html.parser"
        )

        # Find iframe
        iframe = release_soup.find(
            "iframe"
        )

        if not iframe:

            raise ValueError(
                "Release iframe not found"
            )

        iframe_src = iframe.get("src")

        if not iframe_src:

            raise ValueError(
                "Iframe URL not found"
            )

        iframe_url = urljoin(
            BASE_URL,
            iframe_src
        )

        # Request iframe
        iframe_response = session.get(
            iframe_url,
            headers=headers,
            timeout=30
        )

        if iframe_response.status_code != 200:

            raise ValueError(
                f"Iframe status "
                f"{iframe_response.status_code}"
            )

        iframe_soup = BeautifulSoup(
            iframe_response.text,
            "html.parser"
        )

        # Title
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

        # Description
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

        # Ministry
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

        # Convert HTML to plain text
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

        # Validate
        if not title.strip():

            raise ValueError(
                "Title is empty"
            )

        if not text.strip():

            raise ValueError(
                "Text is empty"
            )

        successful += 1

        print(
            "SUCCESS:",
            title[:100]
        )

        print(
            "Ministry:",
            ministry
        )

        print(
            "Text length:",
            len(text)
        )

    except Exception as error:

        failed += 1

        print(
            "FAILED:",
            error
        )


# -----------------------------------------
# STEP 6: Final summary
# -----------------------------------------

print("\n================================")
print("BROWSER-FREE EXTRACTION TEST")
print("================================")

print(
    "URLs found:",
    len(release_urls)
)

print(
    "Successful:",
    successful
)

print(
    "Failed:",
    failed
)

print("================================")