import json
from pathlib import Path

from transformers import AutoTokenizer


INPUT_FILE = "data/processed/government_data_language.jsonl"

MODEL_PATH = "models/pytorch/indic_ner_final/indic_ner_final"

OUTPUT_FILE = "data/final/government_data_tokenized.jsonl"


def load_records():
    records = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def tokenize_records(records):

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH
    )

    print("Tokenizer loaded.")

    for record in records:

        text = record.get("Text", "")

        # Convert text into tokenizer subword tokens
        tokens = tokenizer.tokenize(text)

        record["Tokens"] = tokens

    return records


def save_records(records):

    Path(
        "data/final"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )


def main():

    print("Loading language-detected dataset...")

    records = load_records()

    print(
        "Records loaded:",
        len(records)
    )

    records = tokenize_records(
        records
    )

    print("\nTokenization completed.")

    print("\nToken counts:")

    for record in records:

        print(
            f"{record['ID']}: "
            f"{len(record['Tokens'])} tokens"
        )

    save_records(records)

    print(
        "\nFinal tokenized dataset saved to:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()