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

Government-related textual data was collected from the following sources:

- myScheme
- Press Information Bureau (PIB)
- PM India
- News On AIR
- DD News

The dataset contains both Hindi and English government-related textual records.

### 2. Dataset Size

The final merged dataset contains:

- Hindi: 500 records
- English: 400 records
- Total: 900 records

Source-wise distribution:

- myScheme: 105 records
- PIB: 250 records
- PM India: 200 records
- News On AIR: 200 records
- DD News: 145 records

### 3. Common Schema

All collected records were normalized into a common schema:

- `ID`
- `Title`
- `Text`
- `Source`
- `Url`
- `Language`
- `Category`
- `Department`
- `Date_collected`

### 4. Dataset Merge

All available Hindi and English source datasets were merged into a single standardized dataset.

Output:

`data/processed/government_data_combined.jsonl`

Merge result:

- Total records: **900**
- Duplicate IDs: **0**
- Duplicate URLs: **0**

### 5. Data Validation

Common validation checks were implemented for:

- Required fields
- Duplicate IDs
- Missing values
- URL format
- Date validity
- Dataset schema consistency

Validation result:

- Required fields: Passed
- Duplicate IDs: 0
- Missing values: 0
- Invalid URLs: 0
- Invalid dates: 0

### 6. Data Cleaning

A common cleaning pipeline was implemented to:

- Normalize whitespace
- Normalize spacing around punctuation
- Remove unnecessary leading/trailing whitespace
- Preserve the original meaning of the collected text

Output:

`data/processed/government_data_cleaned.jsonl`

Total cleaned records:

**900**

### 7. Language Detection

Automated text-based language detection was implemented using `langdetect`.

The original `Language` field is preserved as the source/collection language classification.

A separate `Detected_Language` field is added for text-based language auditing.

Declared language distribution:

- Hindi (`hi`): 500
- English (`en`): 400

The language detector flagged 7 records where declared and detected languages differed.

These records are retained and reported as informational audit records because the differences can result from mixed-language content, embedded quotations, or language-detection anomalies.

Output:

`data/processed/government_data_language.jsonl`

### 8. Tokenization

The language-detected dataset was tokenized using the project's Indic tokenizer.

Tokenizer path:

`models/pytorch/indic_ner_final/indic_ner_final`

Tokenization was successfully completed for all 900 records.

Output:

`data/final/government_data_tokenized.jsonl`

Token statistics:

- Minimum tokens: **38**
- Maximum tokens: **23,356**
- Average tokens: **661.95**

### 9. Final Quality Check

The final tokenized dataset was checked for:

- Required fields
- Duplicate IDs
- Empty text
- Empty token lists
- Language detection anomalies
- Token statistics

Quality check results:

- Total records: **900**
- Duplicate IDs: **0**
- Empty text records: **0**
- Empty token lists: **0**
- Language detection audit records: **7**
- Quality check completed successfully

The 7 language-detection differences are treated as **informational audit findings**, not pipeline failures.

---

# Module 1 Data Pipeline

```text
              Government Sources
                     |
       +-------------+-------------+
       |       |       |      |    |
   myScheme   PIB   PM India  News On AIR  DD News
       |       |       |          |          |
       +-------+-------+----------+----------+
                     |
                     v
               Dataset Merge
                     |
                     v
                900 Records
                     |
                     v
                  Cleaning
                     |
                     v
             Data Validation
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