
"""Multilingual keyphrase extraction using YAKE and E5 ranking."""

import re
import unicodedata
from functools import lru_cache
from typing import Dict, List

import numpy as np
import yake
from sentence_transformers import SentenceTransformer


SUPPORTED_LANGUAGES = {"en", "hi", "mr"}
MODEL_NAME = "intfloat/multilingual-e5-base"

TOP_CANDIDATES_PER_N = 20
TOP_KEYPHRASES = 5
DEDUP_LIMIT = 0.9
MAX_PHRASE_WORDS = 6
MAX_DOCUMENT_CHARS = 3000

STOPWORDS = {
    "en": {
        "the", "a", "an", "to", "and", "for", "of", "in",
        "on", "is", "are", "was", "were", "with", "by",
        "from", "this", "that", "as",
    },
    "hi": {
        "और", "के", "की", "का", "को", "से", "में", "पर",
        "ने", "लिए", "यह", "एक", "जो", "या", "है", "हैं",
        "था", "थे", "कर", "करने", "तथा", "भी",
    },
    "mr": {
        "आणि", "च्या", "चे", "ची", "ने", "ला", "ली", "ले",
        "साठी", "मध्ये", "वर", "हा", "ही", "हे", "एक",
        "असे", "यांनी", "यांना", "यांच्या", "तसेच",
    },
}

ACTION_WORDS = {
    "en": {
        "is", "are", "was", "were", "has", "have", "had",
        "will", "would", "can", "could", "should", "must",
        "may", "might", "said", "says", "say", "announced",
        "highlighted", "visited", "visit", "provide", "providing",
        "offers", "offer", "proposes", "proposed", "distributed",
        "distribute", "purchase", "purchasing", "procure",
        "procures", "explore", "pursue", "ensure", "promote",
        "support", "launched", "launch", "launches",
    },
    "hi": {
        "है", "हैं", "था", "थे", "होगा", "होगी", "होंगे",
        "किया", "किए", "करना", "करने", "करते", "करता",
        "करती", "दिया", "दिए", "देना", "देने", "बताया",
        "बताते", "कहा", "कहते", "कहने", "रहा", "रही",
        "रहे", "रहना", "रहने", "बनाने", "बनाया", "मिलने",
        "मिले", "जाएगा", "जाएगी", "जाएंगे",
    },
    "mr": {
        "आहे", "आहेत", "होते", "होता", "होती", "केले",
        "केली", "करण्यात", "करावे", "कराव्यात", "करण्याची",
        "करण्यास", "करण्यासाठी", "दिले", "दिली", "देण्यात",
        "देणे", "सांगितले", "सांगितलं", "म्हणाले", "घेतली",
        "घेतले", "उभारली", "उभारले", "झाले", "झाली",
        "झालेल्या",
    },
}

FUNCTION_WORDS = {
    "en": {
        "in", "on", "at", "for", "from", "with", "by",
        "to", "of", "and", "or", "but", "as",
    },
    "hi": {
        "में", "पर", "से", "के", "की", "का", "को", "और",
        "या", "लिए", "तक", "द्वारा", "साथ", "ने",
    },
    "mr": {
        "मध्ये", "वर", "पासून", "च्या", "चे", "ची", "ला",
        "ली", "ले", "आणि", "किंवा", "साठी",
    },
}

TEMPORAL_WORDS = {
    "en": {"today", "yesterday"},
    "hi": {"आज", "कल"},
    "mr": {"आज", "काल"},
}

INCOMPLETE_HONORIFICS = {
    "hi": {"श्री", "सुश्री", "डॉ", "डॉ."},
    "mr": {"श्री", "सुश्री", "डॉ", "डॉ."},
}

ENTITY_MARKERS = {
    "hi": {
        "श्री", "सुश्री", "डॉ", "प्रधानमंत्री",
        "राष्ट्रपति", "मुख्यमंत्री", "पंडित",
    },
    "mr": {
        "श्री", "सुश्री", "डॉ", "पंतप्रधान",
        "राष्ट्रपती", "मुख्यमंत्री", "पंडित",
        "प्रबोधनकार", "राज्यपाल",
    },
}

KNOWN_ENTITY_PHRASES = {
    "en": {
        "university grants commission",
        "post matric scholarship",
    },
    "hi": {
        "श्री नरेन्‍द्र मोदी",
        "प्रधानमंत्री श्री नरेन्‍द्र मोदी",
    },
    "mr": {
        "पंतप्रधान नरेंद्र मोदी",
        "पंडित दीनदयाल उपाध्याय",
        "केशव सीताराम ठाकरे",
    },
}


INCOMPLETE_ENDINGS = {
    "en": {
        "under", "within", "through", "between",
        "including", "following", "regarding",
        "produced", "provided", "generated",
    },
    "hi": {
        "करके", "देकर", "रखकर", "बनाकर",
        "प्रदान", "तहत", "द्वारा",
    },
    "mr": {
        "आणि", "व", "किंवा", "म्हणून",
        "देऊन", "घेऊन", "करून",
    },
}

HINDI_INCOMPLETE_ENDINGS = {
    "करें", "करना", "करने", "दें", "देना", "प्रदान",
}
HINDI_INCOMPLETE_STARTS = {"तहत", "द्वारा"}

MARATHI_INCOMPLETE_ENDINGS = {
    "आली", "आले", "असली", "असले", "होती", "होते",
    "आहे", "आहेत", "घेतली", "घेतले",
}
MARATHI_NAME_TITLES = {"राज्यपाल", "पंतप्रधान", "राष्ट्रपती"}

PUNCTUATION = " \t\r\n\\\"'`‘’“”()[]{}.,!?;:।॥«»‹›"


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip(PUNCTUATION).strip()


def _validate_input(text: str, language: str) -> None:
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
def _get_extractor(language: str, n: int) -> yake.KeywordExtractor:
    return yake.KeywordExtractor(
        lan=language,
        n=n,
        dedupLim=DEDUP_LIMIT,
        top=TOP_CANDIDATES_PER_N,
        stopwords=STOPWORDS[language],
    )


@lru_cache(maxsize=1)
def _get_e5_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def _clean_title(title: str) -> str:
    title = _normalize(title)
    title = re.sub(
        r"^\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\s*:\s*",
        "",
        title,
    )
    return _normalize(title)


def _phrase_type(phrase: str, language: str) -> str:
    """Heuristically classify a phrase as entity, concept, or fragment."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    phrase = _normalize(phrase)
    if not phrase:
        return "fragment"

    words = phrase.split()
    lower = [word.casefold() for word in words]

    if lower[-1] in INCOMPLETE_ENDINGS[language]:
        return "fragment"

    normalized_key = phrase.casefold()

    known = {
        item.casefold()
        for item in KNOWN_ENTITY_PHRASES[language]
    }
    if normalized_key in known:
        return "entity"

    if len(words) < 2 or len(words) > MAX_PHRASE_WORDS:
        return "fragment"

    if any(word in ACTION_WORDS[language] for word in lower):
        return "fragment"

    # Reject phrases that contain grammatical action fragments.
    if language == "en":
        if lower[0] in {"under", "within", "through", "between"}:
            return "fragment"

    if language == "hi":
        if any(word in lower for word in {"करके", "देकर", "रखकर"}):
            return "fragment"

    if language == "mr":
        if lower[0] in {"भेट", "घेतली", "घेतले"}:
            return "fragment"


    if language == "hi":
        if "ने" in lower:
            return "fragment"
        if lower[-1] in HINDI_INCOMPLETE_ENDINGS:
            return "fragment"
        if lower[0] in HINDI_INCOMPLETE_STARTS:
            return "fragment"

    if language == "mr":
        if lower[-1] in MARATHI_INCOMPLETE_ENDINGS:
            return "fragment"

    if "/" in phrase:
        segments = [part.strip() for part in phrase.split("/")]
        if any(not part for part in segments):
            return "fragment"
        if len(segments) > 1 and len(segments[-1].split()) == 1:
            return "fragment"

    if (
        language in INCOMPLETE_HONORIFICS
        and lower[-1] in INCOMPLETE_HONORIFICS[language]
    ):
        return "fragment"

    if (
        lower[0] in TEMPORAL_WORDS[language]
        or lower[-1] in TEMPORAL_WORDS[language]
    ):
        return "fragment"

    if (
        lower[0] in FUNCTION_WORDS[language]
        or lower[-1] in FUNCTION_WORDS[language]
    ):
        return "fragment"

    if language in ENTITY_MARKERS:
        if any(word in ENTITY_MARKERS[language] for word in words):
            return "entity"

    if language == "mr" and lower[0] in MARATHI_NAME_TITLES:
        return "entity"

    return "concept"


def _generate_candidates(text: str, language: str) -> List[Dict]:
    """Merge YAKE bigram and trigram candidates."""
    candidates = {}

    for n in (2, 3):
        extractor = _get_extractor(language, n)

        for phrase, score in extractor.extract_keywords(text):
            phrase = _normalize(phrase)
            if not phrase:
                continue

            key = phrase.casefold()
            score = float(score)

            if (
                key not in candidates
                or score < candidates[key]["yake_score"]
            ):
                candidates[key] = {
                    "phrase": phrase,
                    "yake_score": score,
                }

    return list(candidates.values())


def _add_title_candidates(
    candidates: List[Dict],
    title: str,
    language: str,
) -> List[Dict]:
    """Explicitly add the complete title and selected title entities."""
    clean_title = _clean_title(title)
    if not clean_title:
        return candidates

    additions = []
    title_words = clean_title.split()

    # Include the complete title only when it is short enough to be a phrase.
    if 2 <= len(title_words) <= MAX_PHRASE_WORDS:
        additions.append(clean_title)

    # News titles can contain a date followed by a role and a person's name.
    if language == "mr":
        for index, word in enumerate(title_words):
            if word in MARATHI_NAME_TITLES:
                candidate = " ".join(
                    title_words[index:index + 4]
                )
                if 2 <= len(candidate.split()) <= MAX_PHRASE_WORDS:
                    additions.append(candidate)

    existing = {
        item["phrase"].casefold()
        for item in candidates
    }


    for phrase in additions:
        key = phrase.casefold()

        if key in existing:
            for item in candidates:
                if item["phrase"].casefold() == key:
                    item["from_title"] = True
            continue

        phrase_type = _phrase_type(phrase, language)
        if phrase_type == "fragment":
            continue

        candidates.append({
            "phrase": phrase,
            "yake_score": 0.05,
            "from_title": True,
        })
        existing.add(key)


        phrase_type = _phrase_type(phrase, language)
        if phrase_type == "fragment":
            continue

        candidates.append({
            "phrase": phrase,
            "yake_score": 0.05,
            "from_title": True,
        })
        existing.add(key)

    return candidates


def _title_overlap(phrase: str, title: str) -> float:
    phrase_tokens = set(_normalize(phrase).casefold().split())
    title_tokens = set(_clean_title(title).casefold().split())

    if not phrase_tokens or not title_tokens:
        return 0.0

    return len(phrase_tokens & title_tokens) / len(phrase_tokens)


def _rank_candidates(
    text: str,
    candidates: List[Dict],
    title: str = "",
) -> List[Dict]:
    """Rank candidates using E5 similarity, YAKE, and title overlap."""
    if not candidates:
        return []

    model = _get_e5_model()
    document = text[:MAX_DOCUMENT_CHARS]

    phrase_embeddings = model.encode(
        ["query: " + item["phrase"] for item in candidates],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    document_embedding = model.encode(
        ["passage: " + document],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]

    similarities = np.dot(phrase_embeddings, document_embedding)

    for item, similarity in zip(candidates, similarities):
        item["e5_score"] = float(similarity)
        yake_component = 1.0 / (1.0 + item["yake_score"])

        type_bonus = {
            "entity": 0.02,
            "concept": 0.01,
        }.get(item["type"], 0.0)\

        title_bonus = 0.08 * _title_overlap(
        item["phrase"],
        title,
        )
        explicit_title_bonus = (
    0.10 if item.get("from_title") else 0.0
)
        item["score"] = (
            0.52 * item["e5_score"]
            + 0.33 * yake_component
            + type_bonus
            + title_bonus
            + explicit_title_bonus
        )

    return sorted(
        candidates,
        key=lambda item: item["score"],
        reverse=True,
    )



def _is_nested_duplicate(candidate: str, selected: List[str]) -> bool:
    """Reject exact duplicates and redundant nested phrases."""
    candidate_norm = _normalize(candidate).casefold()
    candidate_words = candidate_norm.split()

    for existing in selected:
        existing_norm = _normalize(existing).casefold()
        existing_words = existing_norm.split()

        if candidate_norm == existing_norm:
            return True

        # Candidate is already contained inside a selected phrase.
        if len(candidate_words) < len(existing_words):
            for start in range(
                len(existing_words) - len(candidate_words) + 1
            ):
                if (
                    existing_words[
                        start:start + len(candidate_words)
                    ] == candidate_words
                ):
                    return True

        # Reject a longer phrase that only adds one trailing word
        # to an already selected phrase.
        if len(candidate_words) == len(existing_words) + 1:
            for start in range(
                len(candidate_words) - len(existing_words) + 1
            ):
                if (
                    candidate_words[
                        start:start + len(existing_words)
                    ] == existing_words
                ):
                    return True

    return False



def extract_keyphrases(
    text: str,
    language: str,
    title: str = "",
) -> Dict:
    """Extract up to five ranked keyphrases.

    Scores are ranking scores, not probabilities. Title is optional.
    """
    _validate_input(text, language)

    if not isinstance(title, str):
        raise TypeError("title must be a string")

    clean_title = _clean_title(title)
    source_text = (
        f"{clean_title}. {text}"
        if clean_title
        else text
    )

    candidates = _generate_candidates(source_text, language)
    candidates = _add_title_candidates(
        candidates,
        title,
        language,
    )

    filtered = []

    for item in candidates:
        phrase = item["phrase"]
        words = phrase.split()

        if len(words) < 2 or len(words) > MAX_PHRASE_WORDS:
            continue

        if re.search(r"[.!?।॥]", phrase):
            continue

        phrase_type = _phrase_type(phrase, language)
        if phrase_type == "fragment":
            continue

        item["type"] = phrase_type
        filtered.append(item)

    ranked = _rank_candidates(
        source_text,
        filtered,
        title=title,
    )

    keyphrases = []

    for item in ranked:
        selected_phrases = [
            selected["phrase"]
            for selected in keyphrases
        ]

        if _is_nested_duplicate(
            item["phrase"],
            selected_phrases,
        ):
            continue

        keyphrases.append({
            "phrase": item["phrase"],
            "score": round(float(item["score"]), 4),
            "type": item["type"],
        })

        if len(keyphrases) >= TOP_KEYPHRASES:
            break

    return {
        "language": language,
        "text": text,
        "keyphrases": keyphrases,
    }
