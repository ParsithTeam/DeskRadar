# DeskRadar AI Core — Data Directory

This directory contains seed knowledge, historical ticket pools, evaluation datasets, and local vector caches for the AI Core service.

---

## 📁 File Structure & Taxonomy

### 1. Seed Production Data (Knowledge & Baseline Pools)
* **`knowledge_articles.json`:**
  - 11 Persian knowledge-base articles spanning common enterprise IT domains (VPN, email, printer, network, account, hardware, software, permission).
  - Used by the semantic search engine (`app.infrastructure.knowledge_base`) for automatic article suggestions.
* **`old_tickets.json`:**
  - 55 labeled baseline tickets across 8 categories with Iranian organizational terminology.
  - Used as the reference pool for semantic cosine similarity matching and incident clustering.

### 2. Evaluation & Quality Datasets
* **`evaluation_set.json`:**
  - 30 comprehensive evaluation test cases covering normal tickets, edge cases, cross-category queries, and empty inputs.
  - Used by `app.infrastructure.evaluation` to compute offline accuracy, recall, and safety scores.
* **`similarity_pairs.json`:**
  - Pairwise similarity benchmark containing 25 ticket pairs (`eval_001` to `eval_025`) with target similarity scores.
  - Used to evaluate embedding model precision and ranking metrics.
* **`evaluation/analyzer_eval_set.json`:**
  - 50 Persian evaluation tickets for measuring Zero-Shot classification accuracy, intent identification, urgency detection, and response tone.
  - Generated and benchmarked by `scripts/evaluate_analyzer.py`.

### 3. Local Cache Directory
* **`.cache/`:**
  - Contains persistent computed vector embeddings:
    - `ticket_embeddings.json`
    - `article_embeddings.json`
  - Prevents re-computing embeddings on server restarts.
  - Automatically invalidated when ticket/article text changes.
  - Excluded from version control via `.gitignore`.
