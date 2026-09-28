# SentiEdge AI — Project Context

## 1. Project Overview

**Project Title:** SentiEdge AI: An Intelligent Framework for AI-Driven Web Text Mining

**Institution:** Moradabad Institute of Technology  
**Department:** Computer Science and Engineering

SentiEdge AI is an AI-driven multilingual web text mining and analytics platform designed to collect, process, analyze, organize, and visualize textual information obtained from online sources.

The system focuses on multilingual textual data collected from websites, news portals, government portals, and other relevant online sources. The collected data is processed using Natural Language Processing (NLP) techniques and analyzed to identify entities, concepts, keywords, key phrases, semantic relationships, and sentiment.

The extracted information is organized into a knowledge base and presented through an interactive analytics dashboard.

---

## 2. Project Objectives

The major objectives of the project are:

- Collect multilingual textual data from websites, news portals, government portals, and other relevant online sources.
- Validate and clean collected textual data.
- Detect the language of collected text.
- Tokenize and prepare text for downstream NLP processing.
- Perform Named Entity Recognition (NER).
- Discover important concepts from textual data.
- Extract keywords and key phrases.
- Identify semantic relationships between entities and concepts.
- Perform sentiment analysis.
- Store and organize documents, entities, concepts, sentiments, and metadata.
- Provide efficient search, filtering, and information retrieval.
- Develop an interactive analytics dashboard for presenting processed information.
- Generate reports and support data export through the dashboard.

---

# 3. Official Project Modules

The project is divided into four main modules.

---

## Module 1 — Data Ingestion Module

### Objective

The Data Ingestion Module is responsible for collecting and preparing multilingual textual data for downstream NLP and AI processing.

### Responsibilities

- Collect textual data from:
  - Government portals
  - News portals
  - Websites
  - Other relevant online sources
- Validate collected records.
- Clean collected text.
- Detect the language of textual content.
- Tokenize textual data.
- Normalize collected records into a common data structure.
- Prepare a clean and structured dataset for the AI Analytics Engine.

### Current Data Sources

The current dataset collection includes government-related textual information from:

- Press Information Bureau (PIB)
- Prime Minister of India (PM India)
- News On AIR
- DD News
- MyScheme

### Current Languages

The project currently works with:

- Hindi
- English

Additional multilingual expansion may be performed as the project develops.

### Current Dataset Structure

The raw datasets are maintained separately according to source and language.

Examples:

```text
data/raw/
├── pib_raw.jsonl
├── pmindia_hindi_raw.jsonl
├── newsonair_hindi_raw.jsonl
├── ddnews_hindi_raw.jsonl
├── pib_english_raw.jsonl
├── pmindia_english_raw.jsonl
├── newsonair_english_raw.jsonl
├── myscheme_english_raw.jsonl
└── government_data_raw.xlsx