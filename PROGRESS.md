# Project Progress

## Project

SentiEdge AI: An Intelligent Framework for AI-Driven Web Text Mining

## Current Phase

Module 1 — Data Ingestion Module

---

# Module 1 — Data Ingestion Module

**Status:** Implementation Complete — Team Review Pending

## Objective

The objective of Module 1 is to collect multilingual government-related textual data, validate and clean the data, detect language, tokenize the text, and prepare a structured dataset for downstream AI/NLP processing.

---

## Completed Work

### 1. Raw Data Collection

Government-related textual data has been collected from official online sources including:

- Press Information Bureau (PIB)
- Prime Minister of India (PM India)
- News On AIR
- DD News
- MyScheme

The current dataset contains Hindi and English government-related textual records.

The collected data includes government news, announcements, schemes, scheme-related information, and other government-related textual content.

---

### 2. Current Dataset Size

The current raw JSONL datasets contain:

- Hindi: **495 records**
- English: **400 records**
- Total: **895 records**

#### Hindi Distribution

- PIB: **150**
- PM India: **100**
- News On AIR: **100**
- DD News: **145**

**Hindi Total: 495**

#### English Distribution

- PIB: **100**
- PM India: **100**
- News On AIR: **100**
- MyScheme: **100**

**English Total: 400**

### Additional Existing Dataset

An existing MyScheme Excel dataset is also present:

- `data/raw/government_data_raw.xlsx`
- Records: **5**

These 5 records are separate from the current 895-record JSONL collection and are included by the merge pipeline when the file is available.

---

### 3. Raw Dataset Files

Current raw datasets include:

```text
data/raw/
├── government_data_raw.xlsx
├── pib_raw.jsonl
├── pmindia_hindi_raw.jsonl
├── newsonair_hindi_raw.jsonl
├── ddnews_hindi_raw.jsonl
├── pib_english_raw.jsonl
├── pmindia_english_raw.jsonl
├── newsonair_english_raw.jsonl
└── myscheme_english_raw.jsonl