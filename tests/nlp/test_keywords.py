from src.nlp.keywords import extract_keywords


SUPPORTED_LANGUAGES = ["en", "hi", "mr"]


def test_supported_languages():
    text = "Government launched a new scheme."

    for language in SUPPORTED_LANGUAGES:
        if language == "en":
            test_text = text
        elif language == "hi":
            test_text = "सरकार ने नई योजना शुरू की।"
        else:
            test_text = "सरकारने नवीन योजना सुरू केली."

        result = extract_keywords(test_text, language)

        assert result["language"] == language
        assert result["text"] == test_text
        assert isinstance(result["keywords"], list)


def test_empty_text():
    try:
        extract_keywords("", "en")
        assert False
    except ValueError:
        assert True


def test_whitespace_text():
    try:
        extract_keywords("   ", "hi")
        assert False
    except ValueError:
        assert True


def test_invalid_text_type():
    try:
        extract_keywords(123, "en")
        assert False
    except TypeError:
        assert True


def test_invalid_language():
    try:
        extract_keywords("Government launched a scheme.", "fr")
        assert False
    except ValueError:
        assert True


def test_invalid_language_type():
    try:
        extract_keywords("Government launched a scheme.", 123)
        assert False
    except TypeError:
        assert True


def test_output_structure():
    result = extract_keywords(
        "The government launched an agricultural scheme.",
        "en",
    )

    assert set(result.keys()) == {
        "language",
        "text",
        "keywords",
    }

    assert result["language"] == "en"
    assert isinstance(result["text"], str)
    assert isinstance(result["keywords"], list)

    for item in result["keywords"]:
        assert set(item.keys()) == {"keyword", "score"}
        assert isinstance(item["keyword"], str)
        assert isinstance(item["score"], float)


def test_keyword_limit():
    result = extract_keywords(
        "The government launched a new agricultural scheme "
        "to support farmers and rural development.",
        "en",
    )

    assert len(result["keywords"]) <= 10


def test_scores_are_sorted():
    result = extract_keywords(
        "The government launched a new agricultural scheme "
        "to support farmers and rural development.",
        "en",
    )

    scores = [item["score"] for item in result["keywords"]]

    assert scores == sorted(scores)


def test_keywords_are_non_empty():
    result = extract_keywords(
        "The government launched an agricultural scheme.",
        "en",
    )

    for item in result["keywords"]:
        assert item["keyword"].strip() != ""


def test_english_blacklist():
    result = extract_keywords(
        "Click here for the description of today's government scheme.",
        "en",
    )

    keywords = {
        item["keyword"].lower()
        for item in result["keywords"]
    }

    assert "click" not in keywords
    assert "description" not in keywords
    assert "today" not in keywords


def test_hindi_blacklist():
    result = extract_keywords(
        "सरकार को ऐसा करना चाहिए और नई योजना शुरू करनी चाहिए।",
        "hi",
    )

    keywords = {
        item["keyword"]
        for item in result["keywords"]
    }

    assert "चाहिए" not in keywords


def test_marathi_blacklist():
    result = extract_keywords(
        "राज्यपालांनी सांगितले आणि त्यांनी विकासासाठी काम केले.",
        "mr",
    )

    keywords = {
        item["keyword"]
        for item in result["keywords"]
    }

    assert "सांगितले" not in keywords
    assert "त्यांनी" not in keywords
    assert "केले" not in keywords


def test_hindi_extraction():
    result = extract_keywords(
        "सरकार ने किसानों और ग्रामीण विकास के लिए नई कृषि योजना शुरू की।",
        "hi",
    )

    keywords = [item["keyword"] for item in result["keywords"]]

    assert len(keywords) > 0
    assert any(
        keyword in keywords
        for keyword in ["कृषि", "योजना", "किसानों", "ग्रामीण", "विकास"]
    )


def test_marathi_extraction():
    result = extract_keywords(
        "सरकारने शेतकऱ्यांसाठी आणि ग्रामीण विकासासाठी नवीन कृषी योजना सुरू केली.",
        "mr",
    )

    keywords = [item["keyword"] for item in result["keywords"]]

    assert len(keywords) > 0
    assert any(
        keyword in keywords
        for keyword in ["कृषी", "योजना", "ग्रामीण", "विकासासाठी"]
    )