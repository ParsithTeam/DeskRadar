# DeskRadar — AI Core

ServiceDesk Radar AI Core is the intelligent Persian-first core service providing real-time Natural Language Understanding (**Analyzer**) and Semantic Vector Intelligence (**Infrastructure**) for enterprise IT service desks.

---

## 🌟 Capabilities

1. **Unified Pipeline (`POST /analyze`):**
   - **Persian NLP Analysis:** Zero-shot Persian ticket classification, intent detection, urgency scoring, sentiment & frustration analysis, Persian summary generation, and polite suggested response drafting.
   - **Semantic Vector Intelligence:** Semantic ticket similarity search against historical tickets, knowledge base article recommendation, and automated incident candidate detection with duplicate mitigation.
2. **Resilience & Fallback:**
   - Automatic fallback to rule-based Persian keyword matching if deep learning zero-shot classification is unavailable or slow.
   - Degraded-mode responses if vector embedding models or vector databases are offline (service never crashes or blocks the backend).
3. **Modular Endpoints:**
   - Standalone Analyzer API: `POST /analyzer/analyze`
   - Standalone Infrastructure API: `POST /analyze-ticket`
   - System Readiness & Diagnostics: `GET /health`

---

## 📂 Architecture & Directory Layout

```
ai-core/
├── app/
│   ├── main.py                     # Unified FastAPI application entrypoint
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── unified.py              # Unified composite schemas (POST /analyze)
│   │   └── analyzer.py             # Analyzer schemas
│   ├── analyzer/                   # Persian NLP understanding modules
│   │   ├── analyzer_service.py     # Analyzer pipeline orchestrator
│   │   ├── zero_shot_category.py   # Multi-lingual zero-shot Persian classification
│   │   ├── intent_detector.py      # IT domain intent identification
│   │   ├── urgency_detector.py     # Urgency & business impact detection
│   │   ├── sentiment_detector.py   # User frustration & sentiment scoring
│   │   ├── summary_builder.py      # Concise Persian ticket summarizer
│   │   ├── reply_builder.py        # Professional Persian auto-reply generator
│   │   └── normalizer.py           # Persian text cleaning & character normalization
│   ├── infrastructure/             # Semantic vector & incident clustering modules
│   │   ├── embedding_model.py      # Thread-safe sentence embedding singleton
│   │   ├── similarity_search.py    # Cosine similarity matching & pool filtering
│   │   ├── knowledge_base.py       # Knowledge base article retrieval
│   │   ├── incident_detector.py    # Multi-ticket incident detection & deduplication
│   │   └── schemas.py              # Self-contained infrastructure data contracts
│   └── api/routes/                 # Modular API routers
├── config/
│   └── infrastructure_config.json  # Thresholds, model paths, and weights
├── data/                           # Seed tickets, articles, and evaluation datasets
├── docs/                           # Technical documentation & API contracts
│   ├── unified_api_contract.md     # Primary backend integration contract
│   ├── backend_integration_contract.md # Infrastructure contract
│   └── ai_analyzer_quality_report.md
├── scripts/                        # Evaluation, seed, and manual benchmark scripts
└── tests/                          # 37+ automated unit and integration tests
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11 / 3.12 / 3.13)
- Virtual environment with dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Running the Service
From the `ai-core` directory:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 3. Interactive Documentation
Once started, open your browser:
- **Swagger UI:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Health Check:** [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

---

## 🧪 Testing

Run the automated test suite with `pytest`:
```bash
pytest tests -v
```

All 37+ tests covering semantic search, incident detection, zero-shot classification, API endpoints, and resilience will execute.

---

## 📑 API Contract

For detailed request and response payload definitions, refer to [`docs/unified_api_contract.md`](docs/unified_api_contract.md).
