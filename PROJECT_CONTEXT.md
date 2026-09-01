# AKTU AI Edge Project — Project Context

## 1. Project Overview

This project is an AI-powered multilingual knowledge discovery and analytics platform focused on Indian-language textual data.

The system is intended to collect multilingual text from online sources, process and analyze the text using AI/NLP techniques, organize extracted knowledge, provide analytics through an interactive dashboard, and support edge deployment.

---

## 2. Project Objectives

The major objectives of the project are:

- Collect multilingual textual data from relevant online sources.
- Clean and validate collected textual data.
- Detect the language of textual content.
- Tokenize and preprocess the text.
- Perform Named Entity Recognition (NER).
- Perform sentiment analysis.
- Extract concepts, keywords, and key phrases.
- Identify semantic relationships between entities/concepts.
- Store and organize extracted knowledge.
- Provide an interactive analytics/dashboard interface.
- Explore deployment of the AI system on edge hardware.

---

## 3. Development Modules

The project implementation is divided into five modules.

### Module 1 — Data Ingestion Module

Responsibilities:

- Data collection from websites, news portals, government portals, educational documents, online archives, and relevant datasets.
- Data validation.
- Data cleaning.
- Language detection.
- Text tokenization.
- Preparation of a clean dataset for downstream AI processing.

Status: NOT STARTED / UNDER AUDIT

---

### Module 2 — AI Analytics Engine

Responsibilities include:

- Named Entity Recognition (NER).
- Concept discovery.
- Keyword/key-phrase extraction.
- Semantic relationship extraction.
- Sentiment analysis.

An initial Hindi NER baseline already exists in the repository and is being treated as existing development work.

Status: BASELINE EXISTS / NOT COMPLETE

---

### Module 3 — Knowledge Base Management

Responsibilities include:

- Organizing extracted entities and concepts.
- Representing relationships between knowledge elements.
- Knowledge graph / knowledge-base development.
- Semantic search and related knowledge retrieval.

Status: NOT STARTED

---

### Module 4 — Interactive Analytics Dashboard

Responsibilities include:

- Presenting AI analysis results.
- Showing extracted entities and concepts.
- Providing analytics and visualizations.
- Providing an interactive interface for users.

Status: NOT STARTED

---

### Module 5 — Edge Deployment & System Integration

Responsibilities include:

- Integrating the complete AI pipeline.
- Model optimization where required.
- ONNX/runtime-based deployment exploration.
- Edge hardware integration.
- End-to-end system testing.

Status: NOT STARTED

---

## 4. Current Repository State

The GitHub repository contains the basic project structure and an initial NLP/NER implementation.

The existing NLP feature branch contains:

- `src/nlp/train_ner.py`
- `src/nlp/demo_ner.py`

An initial trained NER model is available locally under:

`models/pytorch/indic_ner_final/`

The model contains:

- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`
- `training_args.bin`

The model has been successfully loaded and tested locally.

---

## 5. Existing NER Baseline

The existing NER implementation uses:

- IndicBERT / ALBERT-based token classification architecture.
- Hindi NER data based on the AI4Bharat Naamapadam dataset.
- Seven token-classification labels.
- Hugging Face Transformers.
- Seqeval-based evaluation metrics.

The existing training script uses a limited sample of the dataset for baseline training.

The repository commit claims an F1 score of 87.7%, but this result has not yet been independently reproduced from the current repository state.

Therefore, the existing model is currently treated as a BASELINE and not as the final production model.

---

## 6. Current NER Model Verification

The locally available trained model has been successfully loaded using the Transformers library.

A Hindi test sentence was passed through the NER pipeline and entity predictions were produced.

Example observed predictions included:

- Rahul Gandhi → PERSON
- New Delhi → LOCATION

However, some predictions had low confidence and at least one prediction appeared questionable.

Therefore:

NER inference: WORKING

NER quality: REQUIRES FURTHER EVALUATION

---

## 7. Technology Stack

The repository currently includes/plans to use technologies such as:

- Python
- PyTorch
- Hugging Face Transformers
- Hugging Face Datasets
- Evaluate
- Seqeval
- ONNX
- ONNX Runtime
- Neo4j
- FastAPI
- Uvicorn
- Streamlit

Final technology choices will be recorded in `DECISIONS.md` after the team evaluates them.

---

## 8. Team Development Strategy

The team will primarily work module-by-module.

The agreed development approach is:

Module 1
→ complete and test

Module 2
→ complete and test

Module 3
→ complete and test

Module 4
→ complete and test

Module 5
→ complete and test

A UI prototype may be developed in parallel, but core module completion should not be skipped.

---

## 9. Git/GitHub Strategy

The main branch is the common stable branch.

Each member should work on their own feature/development branch.

Current member branch:

`anubhav-2`

Existing NLP branch:

`feature/nlp-ner-sentiment`

Changes should be tested and reviewed before being merged into `main`.

---

## 10. AI Collaboration Strategy

Gemini, Claude, and ChatGPT may all be used during development.

The project documentation files are intended to maintain a common project context across the team and AI tools.

Before making major changes, the relevant AI assistant should be given:

- `PROJECT_CONTEXT.md`
- `PROGRESS.md`
- `DECISIONS.md`

The AI should not assume that a task is completed unless it is recorded or verified.

---

## 11. Important Current Gaps

The following areas still require development or verification:

- Complete data-ingestion pipeline.
- Actual collected dataset integration.
- Data validation.
- Data cleaning.
- Language detection.
- Project-level tokenization pipeline.
- Proper NER evaluation.
- Verification of the claimed NER F1 score.
- Sentiment analysis.
- Concept and keyword extraction.
- Knowledge base/knowledge graph.
- Analytics dashboard.
- API integration.
- Edge deployment.
- End-to-end testing.

---

## 12. Important Rule

Do not mark a component as COMPLETE merely because code exists.

A component should be marked COMPLETE only after:

1. Implementation exists.
2. It runs successfully.
3. It has been tested.
4. Expected output is verified.
5. The team agrees that the module requirement is satisfied.

---

## 13. Current Project Phase

Current phase:

AUDIT + MODULE 1 PREPARATION

Immediate priority:

Understand and complete the Data Ingestion Module before formally moving to the next module.