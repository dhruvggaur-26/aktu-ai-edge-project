
"""Unified orchestration pipeline for SentiEdge AI."""

from copy import deepcopy
from typing import Any, Dict

from src.nlp.ner import extract_entities
from src.nlp.concepts import discover_concepts
from src.nlp.keywords import extract_keywords
from src.nlp.keyphrases import extract_keyphrases


SUPPORTED_LANGUAGES = {"en", "hi", "mr"}


def process_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Process one government-data record through the available NLP modules.

    Returns original record fields plus an `nlp_results` dictionary.
    Each module is isolated so one failure does not hide other results.
    """

    if not isinstance(record, dict):
        raise TypeError("record must be a dictionary")

    text = record.get("Text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("record must contain non-empty 'Text'")

    raw_language = record.get("Detected_Language") or record.get("Language")
    if not isinstance(raw_language, str):
        raise ValueError(
            "record must contain 'Detected_Language' or 'Language'"
        )

    language = raw_language.strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    title = record.get("Title") or ""
    if not isinstance(title, str):
        title = str(title)

    modules = {
        "ner": lambda: extract_entities(text, language),
        "concepts": lambda: discover_concepts(text, language),
        "keywords": lambda: extract_keywords(text, language),
        "keyphrases": lambda: extract_keyphrases(
            text, language, title=title
        ),
    }

    results = {}
    errors = {}

    for name, run_module in modules.items():
        try:
            results[name] = run_module()
        except Exception as exc:
            results[name] = None
            errors[name] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }

    output = deepcopy(record)
    output["nlp_results"] = {
        "language": language,
        **results,
        "errors": errors,
        "status": "partial" if errors else "success",
    }
    return output

