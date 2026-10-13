# tests/nlp/test_ner.py

import pytest

from src.nlp.ner import (
    extract_entities,
    SUPPORTED_LANGUAGES,
)


# ============================================================
# Basic Interface Tests
# ============================================================

def test_supported_languages():

    assert SUPPORTED_LANGUAGES == {
        "hi",
        "en",
        "mr",
    }


def test_empty_text():

    result = extract_entities(
        "",
        "hi"
    )

    assert result["language"] == "hi"
    assert result["text"] == ""
    assert result["entities"] == []


def test_unsupported_language():

    with pytest.raises(ValueError):

        extract_entities(
            "Hello world",
            "fr"
        )


def test_invalid_text_type():

    with pytest.raises(TypeError):

        extract_entities(
            123,
            "en"
        )


# ============================================================
# Hindi NER
# ============================================================

def test_hindi_person_and_location():

    text = "नरेंद्र मोदी नई दिल्ली में हैं।"

    result = extract_entities(
        text,
        "hi"
    )

    entities = result["entities"]

    assert any(
        entity["text"] == "नरेंद्र मोदी"
        and entity["label"] == "PERSON"
        for entity in entities
    )

    assert any(
        entity["text"] == "नई दिल्ली"
        and entity["label"] == "LOCATION"
        for entity in entities
    )


# ============================================================
# English NER
# ============================================================

def test_english_person_and_location():

    text = "Narendra Modi visited New Delhi."

    result = extract_entities(
        text,
        "en"
    )

    entities = result["entities"]

    assert any(
        entity["text"] == "Narendra Modi"
        and entity["label"] == "PERSON"
        for entity in entities
    )

    assert any(
        entity["text"] == "New Delhi"
        and entity["label"] == "LOCATION"
        for entity in entities
    )


# ============================================================
# Marathi NER
# ============================================================

def test_marathi_person_and_location():

    text = "नरेंद्र मोदी नवी दिल्लीला गेले."

    result = extract_entities(
        text,
        "mr"
    )

    entities = result["entities"]

    assert any(
        entity["text"] == "नरेंद्र मोदी"
        and entity["label"] == "PERSON"
        for entity in entities
    )

    assert any(
        entity["text"] == "नवी दिल्लीला"
        and entity["label"] == "LOCATION"
        for entity in entities
    )


# ============================================================
# Output Structure
# ============================================================

@pytest.mark.parametrize(
    "language,text",
    [
        (
            "hi",
            "नरेंद्र मोदी नई दिल्ली में हैं।"
        ),
        (
            "en",
            "Narendra Modi visited New Delhi."
        ),
        (
            "mr",
            "नरेंद्र मोदी नवी दिल्लीला गेले."
        ),
    ]
)
def test_output_structure(language, text):

    result = extract_entities(
        text,
        language
    )

    assert isinstance(result, dict)

    assert set(result.keys()) == {
        "language",
        "text",
        "entities",
    }

    assert result["language"] == language
    assert result["text"] == text

    assert isinstance(
        result["entities"],
        list
    )

    for entity in result["entities"]:

        assert isinstance(
            entity,
            dict
        )

        assert "text" in entity
        assert "label" in entity

        assert isinstance(
            entity["text"],
            str
        )

        assert isinstance(
            entity["label"],
            str
        )


# ============================================================
# Entity Text Must Exist in Original Text
# ============================================================

@pytest.mark.parametrize(
    "language,text",
    [
        (
            "hi",
            "नरेंद्र मोदी नई दिल्ली में हैं।"
        ),
        (
            "en",
            "Narendra Modi visited New Delhi."
        ),
        (
            "mr",
            "नरेंद्र मोदी नवी दिल्लीला गेले."
        ),
    ]
)
def test_entity_text_exists_in_input(
    language,
    text
):

    result = extract_entities(
        text,
        language
    )

    for entity in result["entities"]:

        assert entity["text"] in text