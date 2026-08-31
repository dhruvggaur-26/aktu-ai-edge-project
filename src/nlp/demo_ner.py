import os
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# 1. Automatically grab the absolute path from your project folder
model_path = os.path.abspath("models/pytorch/indic_ner_final")

# 2. Safety check: Verify the folder exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Error: Cannot find the folder at {model_path}. Please check if it was moved or renamed.")

print(f"Model load ho raha hai from: {model_path}\n")

# 3. Load model and tokenizer locally
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForTokenClassification.from_pretrained(model_path, local_files_only=True)

# 4. Setup the Hugging Face Pipeline
ner_pipeline = pipeline(
    "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
)

# 5. Test sentence
text = "राहुल गांधी कल नई दिल्ली में संसद भवन जाएंगे।"
print(f"Input Sentence: {text}\n")

results = ner_pipeline(text)

# 6. Label translation dictionary
label_map = {
    "LABEL_0": "O (Normal Word)",
    "LABEL_1": "B-PER (Person)",
    "LABEL_2": "I-PER (Person)",
    "LABEL_3": "B-ORG (Organization)",
    "LABEL_4": "I-ORG (Organization)",
    "LABEL_5": "B-LOC (Location)",
    "LABEL_6": "I-LOC (Location)"
}

# 7. Print formatted results
print("Extracted Entities:")
for entity in results:
    readable_label = label_map.get(entity['entity_group'], entity['entity_group'])
    print(
        f"Word: {entity['word']:<15} | Entity: {readable_label:<20} | Score:"
        f" {entity['score']:.2f}"
    )