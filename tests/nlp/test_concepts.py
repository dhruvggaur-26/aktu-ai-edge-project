import pytest

from src.nlp.concepts import (
    MAX_CONCEPTS,
    SUPPORTED_LANGUAGES,
    _chunk_text,
    discover_concepts,
)


# ---------------------------------------------------------------------
# Basic configuration tests
# ---------------------------------------------------------------------

def test_supported_languages():
    assert SUPPORTED_LANGUAGES == {"hi", "en", "mr"}


def test_max_concepts():
    assert MAX_CONCEPTS == 2


# ---------------------------------------------------------------------
# Chunking tests
# ---------------------------------------------------------------------

def test_short_text_single_chunk():
    text = "This is a short government document."

    chunks = _chunk_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_is_chunked():
    text = "a" * 5000

    chunks = _chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 1800 for chunk in chunks)


def test_chunk_overlap():
    text = "a" * 3000

    chunks = _chunk_text(
        text,
        chunk_size=1800,
        overlap=200,
    )

    assert len(chunks) == 2

    # Last 200 characters of first chunk
    # should overlap with first 200 of second.
    assert chunks[0][-200:] == chunks[1][:200]


def test_empty_text_chunking():
    assert _chunk_text("") == []


# ---------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------

def test_empty_text_rejected():
    with pytest.raises(ValueError):
        discover_concepts("", "en")


def test_whitespace_text_rejected():
    with pytest.raises(ValueError):
        discover_concepts("   ", "hi")


def test_invalid_text_type():
    with pytest.raises(TypeError):
        discover_concepts(12345, "en")


def test_invalid_language():
    with pytest.raises(ValueError):
        discover_concepts(
            "This is a government document.",
            "fr",
        )


def test_invalid_language_type():
    with pytest.raises(TypeError):
        discover_concepts(
            "This is a government document.",
            123,
        )


# ---------------------------------------------------------------------
# Real model inference tests
# ---------------------------------------------------------------------

def _validate_output(result, language, original_text):
    assert isinstance(result, dict)

    assert result["language"] == language
    assert result["text"] == original_text

    assert "concepts" in result
    assert isinstance(result["concepts"], list)

    assert 1 <= len(result["concepts"]) <= 2

    for concept in result["concepts"]:
        assert isinstance(concept, dict)

        assert "concept" in concept
        assert "score" in concept

        assert isinstance(concept["concept"], str)
        assert isinstance(concept["score"], float)

        assert concept["concept"].strip() != ""

        assert -1.0 <= concept["score"] <= 1.0


def test_hindi_concept_discovery():
    text = (
        "सरकार ने किसानों की आय बढ़ाने और कृषि क्षेत्र के विकास "
        "के लिए नई योजना शुरू की है।"
    )

    result = discover_concepts(text, "hi")

    _validate_output(result, "hi", text)


def test_english_concept_discovery():
    text = (
        "The government launched a new programme to improve "
        "agricultural productivity and support farmers."
    )

    result = discover_concepts(text, "en")

    _validate_output(result, "en", text)


def test_marathi_concept_discovery():
    text = (
        "सरकारने शेतकऱ्यांच्या उत्पन्नात वाढ करण्यासाठी "
        "आणि कृषी क्षेत्राच्या विकासासाठी नवीन योजना सुरू केली आहे."
    )

    result = discover_concepts(text, "mr")

    _validate_output(result, "mr", text)


# ---------------------------------------------------------------------
# Ranking / output consistency
# ---------------------------------------------------------------------

def test_concepts_are_sorted_by_score():
    text = (
        "The government launched a programme for agricultural "
        "development and farmer support."
    )

    result = discover_concepts(text, "en")

    scores = [
        concept["score"]
        for concept in result["concepts"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_no_duplicate_concepts():
    text = (
        "The government announced a new education and skill "
        "development programme for students and workers."
    )

    result = discover_concepts(text, "en")

    names = [
        concept["concept"]
        for concept in result["concepts"]
    ]

    assert len(names) == len(set(names))