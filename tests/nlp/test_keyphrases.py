
import pytest

from src.nlp import keyphrases as kp


@pytest.mark.parametrize("language", ["en", "hi", "mr"])
def test_supported_languages(language):
    assert language in kp.SUPPORTED_LANGUAGES


@pytest.mark.parametrize("language", ["en", "hi", "mr"])
def test_known_entity_phrases(language):
    phrase = next(iter(kp.KNOWN_ENTITY_PHRASES[language]))
    assert kp._phrase_type(phrase, language) == "entity"


def test_action_phrase_is_fragment():
    assert kp._phrase_type("government launched", "en") == "fragment"


def test_hindi_action_fragment():
    assert kp._phrase_type("प्रधानमंत्री ने प्राकृतिक", "hi") == "fragment"


def test_marathi_valid_concept():
    assert kp._phrase_type("कृषी विकास योजना", "mr") == "concept"


def test_single_word_is_fragment():
    assert kp._phrase_type("scholarship", "en") == "fragment"


def test_normalization():
    assert kp._normalize("  scheme   for farmers. ") == "scheme for farmers"


def test_unsupported_language():
    with pytest.raises(ValueError):
        kp.extract_keyphrases("Some government scheme", "fr")


def test_empty_input():
    with pytest.raises(ValueError):
        kp.extract_keyphrases("", "en")


def test_non_string_input():
    with pytest.raises(TypeError):
        kp.extract_keyphrases(None, "en")


def test_nested_duplicate():
    assert kp._is_nested_duplicate(
        "agricultural development",
        ["new agricultural development scheme"],
    )


def test_non_nested_phrase():
    assert not kp._is_nested_duplicate(
        "farmers welfare scheme",
        ["agricultural development scheme"],
    )

@pytest.mark.parametrize(
    ("text", "language"),
    [
        (
            "The government launched a new agricultural development scheme for farmers.",
            "en",
        ),
        (
            "प्रधानमंत्री ने प्राकृतिक कृषि मिशन की शुरुआत की।",
            "hi",
        ),
        (
            "पंतप्रधानांनी नवीन कृषी विकास योजना सुरू केली.",
            "mr",
        ),
    ],
)
def test_extract_keyphrases_integration(text, language):
    result = kp.extract_keyphrases(text, language)

    assert result["language"] == language
    assert result["text"] == text
    assert isinstance(result["keyphrases"], list)
    assert len(result["keyphrases"]) <= kp.TOP_KEYPHRASES

    for item in result["keyphrases"]:
        assert set(item) == {"phrase", "score", "type"}
        assert isinstance(item["phrase"], str)
        assert isinstance(item["score"], float)
        assert item["type"] in {"entity", "concept"}
