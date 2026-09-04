import requests
from bs4 import BeautifulSoup
from html import unescape
from pathlib import Path
from datetime import date
import json

BASE_URL = "https://www.pib.gov.in"
LIST_URL = "https://www.pib.gov.in/allRel.aspx?reg=48&lang=2"

OUTPUT_FILE = "data/raw/pib_raw.jsonl"


def get_release_links():
    response = requests.get(LIST_URL, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and "PressReleaseDetail.aspx?PRID=" in href:
            if href.startswith("/"):
                href = BASE_URL + href

            if href not in links:
                links.append(href)

    return links


def get_release(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    detail_soup = BeautifulSoup(response.text, "html.parser")

    iframe = detail_soup.find("iframe")

    if not iframe:
        raise ValueError("Release iframe not found")

    iframe_url = iframe.get("src")

    if iframe_url.startswith("/"):
        iframe_url = BASE_URL + iframe_url
    else:
        iframe_url = BASE_URL + "/" + iframe_url

    response = requests.get(iframe_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find(id="ltrTitlee")
    description = soup.find(id="ltrDescriptionn")
    ministry = soup.find(id="MinistryName")

    text = ""

    if description:
        html_text = unescape(description.get("value", ""))

        text = BeautifulSoup(
            html_text,
            "html.parser"
        ).get_text(" ", strip=True)

    return {
        "ID": url.split("PRID=")[-1].split("&")[0],
        "Title": title.get("value", "").strip() if title else "",
        "Text": text,
        "Source": "PIB",
        "Url": url,
        "Language": "hi",
        "Category": "Press Release",
        "Department": ministry.get_text(" ", strip=True)
        if ministry else "",
        "Date_collected": str(date.today()),
    }


def main():
    links = get_release_links()

    print("Release links found:", len(links))

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for url in links:
            try:
                record = get_release(url)

                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

                print(
                    record["ID"],
                    "->",
                    record["Title"][:80]
                )

            except Exception as error:
                print("Failed:", url)
                print("Reason:", error)

    print("\nRaw PIB dataset saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()