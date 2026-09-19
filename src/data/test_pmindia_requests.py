import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LIST_URL = "https://www.pmindia.gov.in/hi/न्यूज-अपडेट्स/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Listing page
response = requests.get(
    LIST_URL,
    headers=headers,
    timeout=30
)

print("Listing status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

base_url = "https://www.pmindia.gov.in"

news_urls = []

for link in soup.find_all("a", href=True):
    href = link["href"]
    title = link.get_text(" ", strip=True)

    if "/hi/news_updates/" in href and title:
        full_url = urljoin(base_url, href)

        if full_url not in news_urls:
            news_urls.append(full_url)

print("News URLs found:", len(news_urls))


# Extract first 10 articles
successful = 0
skipped = 0

for i, news_url in enumerate(news_urls[:10], start=1):

    print("\n" + "=" * 100)
    print(f"ARTICLE {i}")
    print("=" * 100)

    try:
        article_response = requests.get(
            news_url,
            headers=headers,
            timeout=30
        )

        print("Status:", article_response.status_code)

        article_soup = BeautifulSoup(
            article_response.text,
            "html.parser"
        )

        # Article container
        article = article_soup.select_one(
            "#printable .news-bg"
        )

        title_tag = article_soup.select_one(
            "#printable h2"
        )

        date_tag = article_soup.select_one(
            "#printable .share_date"
        )

        # Skip if article structure is missing
        if not article or not title_tag:
            print("SKIPPED: Article structure not found")
            skipped += 1
            continue

        # Title
        title = title_tag.get_text(
            " ",
            strip=True
        )

        # Date
        date = ""

        if date_tag:
            date = date_tag.get_text(
                " ",
                strip=True
            )

        # Full article text
        paragraphs = article.find_all("p")

        text_parts = []

        for paragraph in paragraphs:
            text = paragraph.get_text(
                " ",
                strip=True
            )

            if text:
                text_parts.append(text)

        article_text = " ".join(text_parts)

        if not article_text:
            print("SKIPPED: Article text empty")
            skipped += 1
            continue

        successful += 1

        print("TITLE:")
        print(title)

        print("\nDATE:")
        print(date)

        print("\nURL:")
        print(news_url)

        print("\nTEXT:")
        print(article_text[:1000])

    except Exception as e:
        print("ERROR:", e)
        skipped += 1


print("\n" + "=" * 100)
print("EXTRACTION SUMMARY")
print("=" * 100)

print("Successful articles:", successful)
print("Skipped articles:", skipped)