import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    TrainingArguments, 
    Trainer,
    DataCollatorForTokenClassification
)
import evaluate
import numpy as np

# 1. Configuration and Setup
MODEL_NAME = "ai4bharat/indic-bert"
DATASET_NAME = "ai4bharat/naamapadam"
LANGUAGE = "hi" # Let's start with Hindi for the baseline

print(f"Loading {MODEL_NAME} and {DATASET_NAME} for language: {LANGUAGE}...")

# 2. Load the Dataset and Tokenizer
# The naamapadam dataset provides tags mapping to: 
# 0: 'B-LOC', 1: 'B-ORG', 2: 'B-PER', 3: 'I-LOC', 4: 'I-ORG', 5: 'I-PER', 6: 'O'
dataset = load_dataset(DATASET_NAME, LANGUAGE, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, keep_accents=True)

# 3. Tokenization and Alignment Strategy
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"], 
        truncation=True, 
        is_split_into_words=True,
        max_length=128
    )
    
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100) # Ignore special tokens
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100) # Only label the first sub-token
            previous_word_idx = word_idx
        labels.append(label_ids)
        
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# Map the tokenization over the training and validation sets
tokenized_datasets = dataset.map(tokenize_and_align_labels, batched=True)

# 4. Initialize the Model
# IndicBERT is a multilingual ALBERT model covering 12 major Indian languages.
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=7
)

# 5. Define Evaluation Metrics
seqeval = evaluate.load("seqeval")
label_list = ['B-LOC', 'B-ORG', 'B-PER', 'I-LOC', 'I-ORG', 'I-PER', 'O']

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)
    
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    
    results = seqeval.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# 6. Training Arguments
training_args = TrainingArguments(
    output_dir="../../models/pytorch/indic_ner_checkpoint",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
)

# 7. Initialize Trainer and Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"].select(range(1000)), # Subset for initial testing
    eval_dataset=tokenized_datasets["validation"].select(range(200)),
    processing_class=tokenizer,
    data_collator=DataCollatorForTokenClassification(tokenizer=tokenizer),
    compute_metrics=compute_metrics,
)

print("Starting training...")
trainer.train()

# 8. Save the Final Model for Member 2
trainer.save_model("../../models/pytorch/indic_ner_final")
print("Model saved successfully! Member 2 can now begin ONNX quantization.")