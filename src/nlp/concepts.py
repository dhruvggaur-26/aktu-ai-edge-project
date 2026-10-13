"""
Concept Discovery Engine
------------------------

Module 2 component for semantic concept discovery from multilingual
government text.

Validated configuration:
- Model: intfloat/multilingual-e5-base
- Description weight: 0.6
- Include guidance weight: 0.4
- Chunk size: 1800 characters
- Chunk overlap: 200 characters
- Maximum concepts: 2
- Languages: Hindi, English, Marathi
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import torch
from sentence_transformers import SentenceTransformer, util

from tests.nlp.concept_taxonomy import CONCEPT_TAXONOMY


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

MODEL_NAME = "intfloat/multilingual-e5-base"

SUPPORTED_LANGUAGES = {"hi", "en", "mr"}

DESCRIPTION_WEIGHT = 0.6
INCLUDE_WEIGHT = 0.4

CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200

MAX_CONCEPTS = 2

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------------------------------------------------------------
# Lazy-loaded model
# ---------------------------------------------------------------------

_MODEL: Optional[SentenceTransformer] = None


def get_concept_model() -> SentenceTransformer:
    """
    Load the multilingual E5 model lazily.

    The model is loaded only when concept discovery is actually used.
    """

    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer(
            MODEL_NAME,
            device=DEVICE,
        )

    return _MODEL


# ---------------------------------------------------------------------
# Taxonomy helpers
# ---------------------------------------------------------------------

def _get_concept_names() -> List[str]:
    """Return concept names in deterministic taxonomy order."""

    return [
        concept["name"]
        for concept in CONCEPT_TAXONOMY.values()
    ]


def _get_concept_descriptions() -> List[str]:
    """Return concept descriptions in deterministic taxonomy order."""

    return [
        concept["description"]
        for concept in CONCEPT_TAXONOMY.values()
    ]


def _get_concept_includes() -> List[str]:
    """
    Return include guidance for each concept.

    Include guidance is converted into a single textual representation
    so that it can be embedded by the multilingual E5 model.
    """

    include_texts = []

    for concept in CONCEPT_TAXONOMY.values():
        include_items = concept.get("include", [])

        if isinstance(include_items, list):
            include_text = ", ".join(str(item) for item in include_items)
        else:
            include_text = str(include_items)

        include_texts.append(include_text)

    return include_texts


# ---------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------

def _chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split long text into deterministic overlapping character chunks.

    Short texts remain as a single chunk.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []

    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start += step

    return chunks


# ---------------------------------------------------------------------
# E5 embedding helpers
# ---------------------------------------------------------------------

def _encode_query(
    model: SentenceTransformer,
    texts: List[str],
) -> torch.Tensor:
    """
    Encode document chunks using E5 query formatting.
    """

    formatted = [
        f"query: {text}"
        for text in texts
    ]

    return model.encode(
        formatted,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def _encode_passages(
    model: SentenceTransformer,
    texts: List[str],
) -> torch.Tensor:
    """
    Encode concept descriptions/guidance using E5 passage formatting.
    """

    formatted = [
        f"passage: {text}"
        for text in texts
    ]

    return model.encode(
        formatted,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


# ---------------------------------------------------------------------
# Concept embedding cache
# ---------------------------------------------------------------------

_CONCEPT_EMBEDDINGS: Optional[Dict[str, torch.Tensor]] = None


def _get_concept_embeddings(
    model: SentenceTransformer,
) -> Dict[str, torch.Tensor]:
    """
    Build and cache concept description/include embeddings.

    The same embeddings are reused for every document, avoiding
    repeated taxonomy encoding.
    """

    global _CONCEPT_EMBEDDINGS

    if _CONCEPT_EMBEDDINGS is not None:
        return _CONCEPT_EMBEDDINGS

    names = _get_concept_names()
    descriptions = _get_concept_descriptions()
    includes = _get_concept_includes()

    description_embeddings = _encode_passages(
        model,
        descriptions,
    )

    include_embeddings = _encode_passages(
        model,
        includes,
    )

    _CONCEPT_EMBEDDINGS = {}

    for index, name in enumerate(names):
        _CONCEPT_EMBEDDINGS[name] = {
            "description": description_embeddings[index],
            "include": include_embeddings[index],
        }

    return _CONCEPT_EMBEDDINGS


# ---------------------------------------------------------------------
# Document embedding
# ---------------------------------------------------------------------

def _get_document_embedding(
    model: SentenceTransformer,
    text: str,
) -> torch.Tensor:
    """
    Create one normalized document embedding by mean-pooling
    normalized chunk embeddings.
    """

    chunks = _chunk_text(text)

    if not chunks:
        raise ValueError("text must not be empty")

    chunk_embeddings = _encode_query(
        model,
        chunks,
    )

    document_embedding = chunk_embeddings.mean(dim=0)

    document_embedding = torch.nn.functional.normalize(
        document_embedding,
        p=2,
        dim=0,
    )

    return document_embedding


# ---------------------------------------------------------------------
# Concept scoring
# ---------------------------------------------------------------------

def _score_concepts(
    document_embedding: torch.Tensor,
    concept_embeddings: Dict[str, Dict[str, torch.Tensor]],
) -> List[Dict[str, Any]]:
    """
    Calculate hybrid concept scores.

    final_score =
        0.6 * description_similarity
        +
        0.4 * include_similarity
    """

    results: List[Dict[str, Any]] = []

    for concept_name, embeddings in concept_embeddings.items():

        description_score = float(
            util.cos_sim(
                document_embedding,
                embeddings["description"],
            ).item()
        )

        include_score = float(
            util.cos_sim(
                document_embedding,
                embeddings["include"],
            ).item()
        )

        final_score = (
            DESCRIPTION_WEIGHT * description_score
            + INCLUDE_WEIGHT * include_score
        )

        results.append(
            {
                "concept": concept_name,
                "score": round(final_score, 4),
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def discover_concepts(
    text: str,
    language: str,
) -> Dict[str, Any]:
    """
    Discover the top semantic concepts from a multilingual document.

    Parameters
    ----------
    text:
        Input document text.

    language:
        Language code:
        - hi = Hindi
        - en = English
        - mr = Marathi

    Returns
    -------
    dict
        Example:

        {
            "language": "hi",
            "text": "...",
            "concepts": [
                {
                    "concept": "Agriculture & Rural Development",
                    "score": 0.8123
                },
                {
                    "concept": "Economy & Finance",
                    "score": 0.7741
                }
            ]
        }
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not text.strip():
        raise ValueError("text must not be empty")

    if not isinstance(language, str):
        raise TypeError("language must be a string")

    language = language.lower().strip()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {sorted(SUPPORTED_LANGUAGES)}"
        )

    model = get_concept_model()

    document_embedding = _get_document_embedding(
        model,
        text,
    )

    concept_embeddings = _get_concept_embeddings(
        model,
    )

    ranked_concepts = _score_concepts(
        document_embedding,
        concept_embeddings,
    )

    selected_concepts = ranked_concepts[:MAX_CONCEPTS]

    return {
        "language": language,
        "text": text,
        "concepts": selected_concepts,
    }


# ---------------------------------------------------------------------
# Cache reset helper
# ---------------------------------------------------------------------

def reset_concept_cache() -> None:
    """
    Reset cached model and concept embeddings.

    Mainly useful for testing.
    """

    global _MODEL
    global _CONCEPT_EMBEDDINGS

    _MODEL = None
    _CONCEPT_EMBEDDINGS = None