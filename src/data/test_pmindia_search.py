import requests
from bs4 import BeautifulSoup

KEYWORD = "प्रधानमंत्री"

all_urls = set()

for page in range(1, 6):

    if page == 1:
        url = f"https://www.pmindia.gov.in/hi/?s={KEYWORD}"
    else:
        url = f"https://www.pmindia.gov.in/hi/page/{page}/?s={KEYWORD}"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )

    soup = BeautifulSoup(response.text, "html.parser")

    page_urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/hi/news_updates/" in href:
            page_urls.add(href)

    print(f"Page {page}: {len(page_urls)} URLs")

    all_urls.update(page_urls)

print("\n==============================")
print("Total unique URLs:", len(all_urls))
print("==============================")