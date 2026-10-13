# src/nlp/ner.py

from typing import Dict, List

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "ai4bharat/IndicNER"

SUPPORTED_LANGUAGES = {
    "hi",  # Hindi
    "en",  # English
    "mr",  # Marathi
}


# ============================================================
# IndicNER Label Mapping
# ============================================================

LABEL_MAP = {
    "B-PER": "PERSON",
    "I-PER": "PERSON",

    "B-ORG": "ORGANIZATION",
    "I-ORG": "ORGANIZATION",

    "B-LOC": "LOCATION",
    "I-LOC": "LOCATION",

    "O": "O",
}


# ============================================================
# IndicNER Model
# ============================================================

class IndicNER:
    """
    AI4Bharat IndicNER wrapper.

    Supported languages:
        hi -> Hindi
        en -> English
        mr -> Marathi

    Supported entity types:
        PERSON
        ORGANIZATION
        LOCATION
    """

    def __init__(self):

        # ----------------------------------------------------
        # Select device
        # ----------------------------------------------------

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print(
            f"Loading IndicNER on: {self.device}"
        )

        # ----------------------------------------------------
        # Load tokenizer
        # ----------------------------------------------------

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True
        )

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        self.model = AutoModelForTokenClassification.from_pretrained(
            MODEL_NAME
        )

        self.model.to(self.device)

        self.model.eval()

        print(
            "IndicNER loaded successfully."
        )

    # ========================================================
    # Extract Entities
    # ========================================================

    def extract_entities(
        self,
        text: str,
        language: str
    ) -> Dict:

        # ----------------------------------------------------
        # Validate language
        # ----------------------------------------------------

        if language not in SUPPORTED_LANGUAGES:

            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: "
                f"{sorted(SUPPORTED_LANGUAGES)}"
            )

        # ----------------------------------------------------
        # Validate text
        # ----------------------------------------------------

        if not isinstance(text, str):

            raise TypeError(
                "text must be a string"
            )

        # ----------------------------------------------------
        # Empty text
        # ----------------------------------------------------

        if not text.strip():

            return {
                "language": language,
                "text": text,
                "entities": []
            }

        # ----------------------------------------------------
        # Tokenize
        # ----------------------------------------------------

        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_offsets_mapping=True,
        )

        # ----------------------------------------------------
        # Word IDs
        #
        # Example:
        #
        # "नरेंद्र मोदी"
        #
        # multiple tokenizer pieces can belong to the
        # same original word.
        #
        # word_ids() allows us to reconstruct the
        # original words correctly.
        # ----------------------------------------------------

        word_ids = encoded.word_ids(
            batch_index=0
        )

        # ----------------------------------------------------
        # Offset mapping
        # ----------------------------------------------------

        offset_mapping = encoded[
            "offset_mapping"
        ][0]

        # ----------------------------------------------------
        # Prepare model inputs
        # ----------------------------------------------------

        inputs = {
            key: value.to(self.device)
            for key, value in encoded.items()
            if key != "offset_mapping"
        }

        # ----------------------------------------------------
        # Model inference
        # ----------------------------------------------------

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        # ----------------------------------------------------
        # Get predicted class for every token
        # ----------------------------------------------------

        predictions = torch.argmax(
            outputs.logits,
            dim=-1
        )[0]

        # ====================================================
        # STEP 1
        # Group tokenizer pieces by original word
        # ====================================================

        words = {}

        for token_index, word_id in enumerate(word_ids):

            # Special tokens
            if word_id is None:
                continue

            word_id = int(word_id)

            # ------------------------------------------------
            # Model label
            # ------------------------------------------------

            label = self.model.config.id2label[
                predictions[token_index].item()
            ]

            mapped_label = LABEL_MAP.get(
                label,
                "O"
            )

            # ------------------------------------------------
            # Character offsets
            # ------------------------------------------------

            start = int(
                offset_mapping[token_index][0]
            )

            end = int(
                offset_mapping[token_index][1]
            )

            # ------------------------------------------------
            # Ignore invalid offsets
            # ------------------------------------------------

            if end <= start:
                continue

            # ------------------------------------------------
            # Create word entry
            # ------------------------------------------------

            if word_id not in words:

                words[word_id] = {
                    "start": start,
                    "end": end,
                    "labels": []
                }

            # ------------------------------------------------
            # Store label
            # ------------------------------------------------

            words[word_id]["labels"].append(
                mapped_label
            )

            # ------------------------------------------------
            # Update character span
            # ------------------------------------------------

            words[word_id]["start"] = min(
                words[word_id]["start"],
                start
            )

            words[word_id]["end"] = max(
                words[word_id]["end"],
                end
            )

        # ====================================================
        # STEP 2
        # Determine entity type for every original word
        # ====================================================

        word_entities = []

        for word_id in sorted(words.keys()):

            word_info = words[word_id]

            labels = word_info["labels"]

            # ------------------------------------------------
            # Count entity labels
            #
            # We intentionally do not depend strictly on
            # B/I because IndicNER can output multiple B
            # labels for subword pieces of one Indian-language
            # word.
            # ------------------------------------------------

            entity_labels = [
                label
                for label in labels
                if label != "O"
            ]

            # ------------------------------------------------
            # No entity
            # ------------------------------------------------

            if not entity_labels:

                word_entities.append({
                    "text": text[
                        word_info["start"]:
                        word_info["end"]
                    ],
                    "label": "O"
                })

                continue

            # ------------------------------------------------
            # Count labels
            # ------------------------------------------------

            label_counts = {}

            for label in entity_labels:

                label_counts[label] = (
                    label_counts.get(label, 0) + 1
                )

            # ------------------------------------------------
            # Select majority entity type
            # ------------------------------------------------

            entity_type = max(
                label_counts,
                key=label_counts.get
            )

            # ------------------------------------------------
            # Recover original word
            # ------------------------------------------------

            word_text = text[
                word_info["start"]:
                word_info["end"]
            ]

            word_entities.append({
                "text": word_text,
                "label": entity_type
            })

        # ====================================================
        # STEP 3
        # Merge consecutive entity words
        # ====================================================

        entities: List[Dict] = []

        current_entity = None

        for word in word_entities:

            # ------------------------------------------------
            # Outside entity
            # ------------------------------------------------

            if word["label"] == "O":

                if current_entity is not None:

                    entities.append(
                        current_entity
                    )

                    current_entity = None

                continue

            # ------------------------------------------------
            # Start new entity
            # ------------------------------------------------

            if current_entity is None:

                current_entity = {
                    "text": word["text"],
                    "label": word["label"]
                }

                continue

            # ------------------------------------------------
            # Same entity type
            # ------------------------------------------------

            if (
                current_entity["label"]
                == word["label"]
            ):

                current_entity["text"] += (
                    " " + word["text"]
                )

            # ------------------------------------------------
            # Different entity type
            # ------------------------------------------------

            else:

                entities.append(
                    current_entity
                )

                current_entity = {
                    "text": word["text"],
                    "label": word["label"]
                }

        # ----------------------------------------------------
        # Add final entity
        # ----------------------------------------------------

        if current_entity is not None:

            entities.append(
                current_entity
            )

        # ====================================================
        # Final result
        # ====================================================

        return {
            "language": language,
            "text": text,
            "entities": entities
        }


# ============================================================
# Singleton Model
# ============================================================

_ner_model = None


def get_ner_model() -> IndicNER:
    """
    Load the IndicNER model only once.

    This prevents loading the large model every time
    extract_entities() is called.
    """

    global _ner_model

    if _ner_model is None:

        _ner_model = IndicNER()

    return _ner_model


# ============================================================
# Convenience Function
# ============================================================

def extract_entities(
    text: str,
    language: str
) -> Dict:
    """
    Convenience function for NER extraction.
    """

    model = get_ner_model()

    return model.extract_entities(
        text=text,
        language=language
    )


# ============================================================
# Manual Testing
# ============================================================

if __name__ == "__main__":

    test_cases = [

        # Hindi
        (
            "hi",
            "नरेंद्र मोदी नई दिल्ली में हैं।"
        ),

        # English
        (
            "en",
            "Narendra Modi visited New Delhi."
        ),

        # Marathi
        (
            "mr",
            "नरेंद्र मोदी नवी दिल्लीला गेले."
        ),
    ]

    for language, text in test_cases:

        print("\n" + "=" * 60)

        print(
            f"Language: {language}"
        )

        print(
            f"Text: {text}"
        )

        print("=" * 60)

        result = extract_entities(
            text=text,
            language=language
        )

        print(result)