# Project Progress

## Project
AKTU AI Edge Project

## Current Phase

Module 1 — Data Ingestion Module

---

# Module 1 — Data Ingestion Module

**Status:** Implementation Complete — Team Review Pending

## Objective

The objective of Module 1 is to collect government-related textual data, validate and clean the data, detect language, tokenize the text, and prepare a structured dataset for downstream AI processing.

---

## Completed Work

### 1. Raw Data Collection

Two government-related sources were used for the initial dataset:

- myScheme
- Press Information Bureau (PIB)

### 2. myScheme Dataset

- Collected 5 government scheme records.
- Stored the raw dataset in Excel format.
- File:

`data/raw/government_data_raw.xlsx`

### 3. PIB Dataset

- Collected 103 Hindi PIB press releases.
- PIB release listing was processed using requests and BeautifulSoup.
- Release title, text, department, source URL, language, category, and collection date were extracted.
- File:

`data/raw/pib_raw.jsonl`

### 4. Common Schema

Both datasets were verified to follow the same schema:

- `ID`
- `Title`
- `Text`
- `Source`
- `Url`
- `Language`
- `Category`
- `Department`
- `Date_collected`

### 5. Dataset Merge

The two sources were merged into a single standardized dataset.

Dataset size:

- myScheme: 5 records
- PIB: 103 records
- Combined: 108 records
- Unique IDs: 108

Output:

`data/processed/government_data_combined.jsonl`

### 6. Data Validation

Validation checks were implemented for:

- Required columns/fields
- Duplicate IDs
- Missing values
- URL format
- Date validity
- Dataset schema consistency

The combined dataset passed validation checks with no duplicate IDs, missing values, invalid URLs, or invalid dates.

### 7. Data Cleaning

A cleaning pipeline was implemented to:

- Normalize whitespace
- Normalize line breaks
- Remove unnecessary spaces around punctuation
- Normalize punctuation
- Remove leading and trailing whitespace

Output:

`data/processed/government_data_cleaned.jsonl`

Total cleaned records:

**108**

### 8. Language Detection

Automated language detection was implemented using `langdetect`.

Results:

- Total records: 108
- Hindi (`hi`): 108
- Other languages: 0

Output:

`data/processed/government_data_language.jsonl`

### 9. Tokenization

The cleaned government text was tokenized using the project's IndicBERT tokenizer.

Tokenizer path:

`models/pytorch/indic_ner_final/indic_ner_final`

Tokenization was successfully completed for all 108 records.

Output:

`data/final/government_data_tokenized.jsonl`

### 10. Final Quality Check

The final tokenized dataset was checked for:

- Required fields
- Duplicate IDs
- Empty text
- Empty token lists
- Language mismatches
- Token statistics

Validation results:

- Total records: **108**
- Unique IDs: **108**
- Empty text records: **0**
- Empty token lists: **0**
- Language mismatches: **0**
- Hindi records: **108**
- Minimum tokens per record: **47**
- Maximum tokens per record: **3933**
- Average tokens per record: **833.68**

The final quality check completed successfully.

---

# Module 1 Data Pipeline

```text
        Government Sources

                 |
       +-------------------+
       |                   |
    myScheme              PIB
    5 records           103 records
       |                   |
       +---------+---------+
                 |
                 v
          Dataset Merge
                 |
                 v
            108 Records
                 |
                 v
              Cleaning
                 |
                 v
        Language Detection
                 |
                 v
           Tokenization
                 |
                 v
          Quality Check
                 |
                 v
          Final Dataset