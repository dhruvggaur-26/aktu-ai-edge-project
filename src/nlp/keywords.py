"""
Keyword Extraction using YAKE.

Supported languages:
- English (en)
- Hindi (hi)
- Marathi (mr)
"""

from functools import lru_cache
from typing import Dict, List

from yake import KeywordExtractor


SUPPORTED_LANGUAGES = {"en", "hi", "mr"}

TOP_K = 10
NGRAM_SIZE = 1
DEDUP_LIMIT = 0.9


STOPWORDS = {
    "en": {
        "the", "a", "an", "to", "and", "for", "of", "in", "on",
        "is", "are", "was", "were", "with", "by", "from", "this",
        "that", "as",
    },
    "hi": {
        "और", "के", "की", "का", "को", "से", "में", "पर", "ने",
        "लिए", "यह", "एक", "जो", "या", "है", "हैं", "था",
        "थे", "कर", "करने", "तथा", "भी",
    },
    "mr": {
        "आणि", "च्या", "चे", "ची", "ने", "ला", "ली", "ले",
        "साठी", "मध्ये", "वर", "हा", "ही", "हे", "एक", "असे",
        "यांनी", "यांना", "यांच्या", "तसेच",
    },
}


BLACKLIST = {
    "en": {
        "click",
        "description",
        "today",
        "yesterday",
    },
    "hi": {
        "चाहिए",
    },
    "mr": {
        "आहे",
        "केले",
        "सांगितले",
        "त्यांनी",
        "करण्यात",
        "आहेत",
        "होते",
        "यावेळी",
        "आले",
        "म्हणाले",
        "केली",
        "यांची",
        "दिली",
    },
}


def _validate_input(text: str, language: str) -> None:
    """Validate keyword extraction input."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not isinstance(language, str):
        raise TypeError("language must be a string")

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {sorted(SUPPORTED_LANGUAGES)}"
        )

    if not text.strip():
        raise ValueError("text must not be empty")


@lru_cache(maxsize=3)
def _get_extractor(language: str) -> KeywordExtractor:
    """
    Create and cache one YAKE extractor per language.

    Extractors are cached because the same language is processed
    repeatedly when running over the full 1202-record dataset.
    """

    return KeywordExtractor(
        lan=language,
        n=NGRAM_SIZE,
        dedup_lim=DEDUP_LIMIT,
        top=TOP_K,
        stopwords=STOPWORDS[language],
    )


def _normalize_keyword(keyword: str) -> str:
    """Normalize extracted keyword text and remove surrounding punctuation."""

    keyword = keyword.strip()

    # Remove punctuation/symbols from the beginning and end,
    # while preserving internal characters such as hyphens.
    keyword = keyword.strip(
        ".,!?;:'\"()[]{}<>।,॥:;!?\"'“”‘’"
    )

    return " ".join(keyword.split())

def _is_valid_keyword(keyword: str, language: str) -> bool:
    """Apply final keyword-level filtering."""

    normalized = _normalize_keyword(keyword)
    comparison = normalized.lower()

    if not normalized:
        return False

    # Remove one-character candidates.
    if len(normalized) <= 1:
        return False

    # Remove language-specific blacklist entries.
    if comparison in BLACKLIST[language]:
        return False

    # Remove exact stopwords that may still appear as candidates.
    if comparison in STOPWORDS[language]:
        return False

    return True


def extract_keywords(text: str, language: str) -> Dict:
    """
    Extract keywords from multilingual text using YAKE.

    Args:
        text: Input document text.
        language: ISO-style language code: en, hi, or mr.

    Returns:
        Dictionary containing:
        - language
        - text
        - keywords

    Example:
        {
            "language": "en",
            "text": "Government launched a new scheme.",
            "keywords": [
                {"keyword": "government", "score": 0.1234},
                {"keyword": "scheme", "score": 0.2345}
            ]
        }
    """

    _validate_input(text, language)

    extractor = _get_extractor(language)

    raw_keywords = extractor.extract_keywords(text)

    keywords: List[Dict] = []

    for keyword, score in raw_keywords:
        normalized = _normalize_keyword(keyword)

        if not _is_valid_keyword(normalized, language):
            continue

        keywords.append(
            {
                "keyword": normalized,
                "score": round(float(score), 4),
            }
        )

    return {
        "language": language,
        "text": text,
        "keywords": keywords,
    }