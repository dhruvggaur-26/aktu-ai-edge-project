import pytest

from src.nlp import pipeline


def sample_record():
    return {
        "ID": 101,
        "Title": "Government agriculture scheme",
        "Text": "The government announced support for farmers.",
        "Detected_Language": "en",
        "Source": "test",
    }


def test_process_record_combines_all_modules(monkeypatch):
    monkeypatch.setattr(
        pipeline, "extract_entities",
        lambda text, language: {"entities": [{"text": "government"}]},
    )
    monkeypatch.setattr(
        pipeline, "discover_concepts",
        lambda text, language: {"concepts": [{"concept": "Agriculture"}]},
    )
    monkeypatch.setattr(
        pipeline, "extract_keywords",
        lambda text, language: {"keywords": [{"keyword": "farmers"}]},
    )
    monkeypatch.setattr(
        pipeline, "extract_keyphrases",
        lambda text, language, title="": {
            "keyphrases": [{"phrase": "support for farmers"}]
        },
    )

    record = sample_record()
    result = pipeline.process_record(record)

    assert result["nlp_results"]["status"] == "success"
    assert result["nlp_results"]["errors"] == {}
    assert result["nlp_results"]["ner"]["entities"]
    assert result["nlp_results"]["concepts"]["concepts"]
    assert result["nlp_results"]["keywords"]["keywords"]
    assert result["nlp_results"]["keyphrases"]["keyphrases"]
    assert result["ID"] == record["ID"]
    assert result["Title"] == record["Title"]


def test_process_record_handles_module_failure(monkeypatch):
    def fail_ner(text, language):
        raise RuntimeError("NER test failure")

    monkeypatch.setattr(pipeline, "extract_entities", fail_ner)
    monkeypatch.setattr(
        pipeline, "discover_concepts",
        lambda text, language: {"concepts": []},
    )
    monkeypatch.setattr(
        pipeline, "extract_keywords",
        lambda text, language: {"keywords": []},
    )
    monkeypatch.setattr(
        pipeline, "extract_keyphrases",
        lambda text, language, title="": {"keyphrases": []},
    )

    result = pipeline.process_record(sample_record())
    nlp = result["nlp_results"]

    assert nlp["status"] == "partial"
    assert nlp["ner"] is None
    assert nlp["errors"]["ner"]["type"] == "RuntimeError"
    assert nlp["concepts"] == {"concepts": []}
    assert nlp["keywords"] == {"keywords": []}
    assert nlp["keyphrases"] == {"keyphrases": []}


def test_process_record_accepts_language_fallback(monkeypatch):
    monkeypatch.setattr(
        pipeline, "extract_entities",
        lambda text, language: {"entities": []},
    )
    monkeypatch.setattr(
        pipeline, "discover_concepts",
        lambda text, language: {"concepts": []},
    )
    monkeypatch.setattr(
        pipeline, "extract_keywords",
        lambda text, language: {"keywords": []},
    )
    monkeypatch.setattr(
        pipeline, "extract_keyphrases",
        lambda text, language, title="": {"keyphrases": []},
    )

    record = sample_record()
    record.pop("Detected_Language")
    record["Language"] = "EN"

    result = pipeline.process_record(record)

    assert result["nlp_results"]["language"] == "en"
    assert result["nlp_results"]["status"] == "success"


@pytest.mark.parametrize(
    "record",
    [
        {},
        {"Text": "Some text"},
        {"Text": "   ", "Language": "en"},
        {"Text": "Some text", "Language": "fr"},
    ],
)
def test_process_record_rejects_invalid_input(record):
    with pytest.raises((TypeError, ValueError)):
        pipeline.process_record(record)
