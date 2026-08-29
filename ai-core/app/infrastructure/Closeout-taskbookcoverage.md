# ServiceDesk Radar — AI Infrastructure: Close-Out & Taskbook Coverage

**Scope of this work:** `ai-core/app/infrastructure/` and its config/data/scripts —
i.e. the **Infrastructure Intelligence AI** (Taskbook §9), plus the infrastructure
portions of Core-AI API (§10) and seed/KB data (§11). Everything else in the
Taskbook (Frontend §5, Backend §6, Database §7, Analyzer AI §8, DevOps §12, QA §13)
is **out of scope** and owned by other team members.

Status: **the AI Infrastructure scope is implemented and self-validated**. The
default Python-cosine path is verified, Qdrant remains intentionally disabled,
all 22 automated tests pass, and the real-model report records a `0.5914`
separation gap and `0.9333` retrieval category accuracy.

---

## 1. Taskbook §9 — Infrastructure Intelligence AI (OUR SCOPE)

### §9.3 Embedding Pipeline
| Taskbook task | Status | Where |
|---|---|---|
| Load embedding model once at startup | ✅ | `embedding_model.py` (singleton, loaded in startup) |
| Build standardized ticket text | ✅ | `build_ticket_text()` |
| Encode new ticket → vector | ✅ | `EmbeddingModel.encode()` / `encode_batch()` |
| Store embedding (don't re-embed unless text changes) | ✅ | persistent article and ticket-vector caches, keyed by text hash + model version |
| Record `embedding_model_version` | ✅ | `model_version` → `InfrastructureResult` / health |

### §9.4 Similar Ticket Search
| Taskbook task | Status | Where |
|---|---|---|
| `find_similar_tickets` → top-5 sorted | ✅ | `similarity_search.py` |
| Filter deleted/closed tickets | ✅ | `EXCLUDED_STATUSES` |
| Store similarity score | ✅ | `SimilarTicket.similarity` |
| Threshold from config | ✅ | `similarity.threshold_similar` / `threshold_very_similar` |
| Self-match guard | ✅ | `query_ticket_id` excluded |
| Test with Persian dataset | ✅ | `test_persian_pipeline.py` validates VPN and printer requests over the full Persian dataset |

### §9.5 Knowledge Base Retrieval
| Taskbook task | Status | Where |
|---|---|---|
| Article structure + ≥10 seed articles | ✅ | `data/knowledge_articles.json` (11) |
| Build article embeddings | ✅ | `build_article_embeddings()` |
| `find_related_article` (VPN→VPN) | ✅ | `knowledge_base.py` |
| Apply minimum score floor | ✅ | `article_score_min` |
| Connect to suggested reply | ✅ (interface) | returns `RelatedArticle.title`; reply-builder wiring is Analyzer-side |

### §9.6 Incident Candidate Detection
| Taskbook task | Status | Where |
|---|---|---|
| Incident rule (count/category/score/severity) | ✅ | `incident_detector.py` |
| Detect medium (2–3) | ✅ | config bands |
| Detect high (≥4) | ✅ | config bands |
| Persian incident title | ✅ | `fa_title_incident` |
| Persian incident reason | ✅ | `fa_reason_incident` (Persian digits) |
| Avoid duplicate incident | ✅ | cluster-overlap dedup via `open_incidents`, returning `duplicate_incident_id` |

### §9.7 Qdrant (optional)
| Taskbook task | Status | Where |
|---|---|---|
| Qdrant service in Docker | ➖ DevOps §12 | adapter ready; compose is DevOps scope |
| Create `tickets` collection | ✅ | `ensure_collections()` |
| Upsert tickets | ✅ | `upsert()` (+ orchestrator seed upsert) |
| Search in Qdrant | ✅ | `search()` + similarity/KB Qdrant paths |
| Fallback without Qdrant | ✅ | Python cosine default (Rule 8) |

### §9.8 Evaluation & Threshold Tuning
| Taskbook task | Status | Where |
|---|---|---|
| `evaluation_set.json` (≥50) | ✅ | 60 labeled tickets |
| Similarity ground truth | ✅ | `similarity_pairs.json` (23+22) |
| Retrieval category accuracy | ✅ | `eval_retrieval_category_accuracy()`; Analyzer accuracy is a joint integration metric |
| Similarity quality | ✅ | `eval_similarity_quality()` |
| Choose final threshold | ✅ | `eval_threshold_sweep()` |
| Quality report for README / `docs/evaluation.md` | ✅ | `scripts/evaluate_infrastructure.py` |

### §10 Core-AI API (infrastructure portion)
| Taskbook task | Status | Where |
|---|---|---|
| `POST /analyze-ticket` (infra block) | ✅ | `app/main.py` → `run_infrastructure` |
| `GET /health` | ✅ | `app/main.py` (200 ok/degraded, 503 error) |
| Model loaded at startup, not per request | ✅ | lifespan + singleton |
| Latency captured | ✅ | `latency_ms` |
| Controlled model errors (no raw exception to Backend) | ✅ | never-raise contract |
| `TicketAnalysisRequest/Response` (combined analyzer+infra) | ➖ Core/Analyzer | combination layer is outside infra scope |

---

## 2. Current status and deferred follow-ups

1. **Dependencies and file placement** — ✅ complete at the repository paths listed in §4.
2. **Test suite** — ✅ 22 tests cover cache persistence, Persian VPN/printer retrieval, incident deduplication, controlled errors, config validation, and Rule 6.
3. **Real-model evaluation** — ✅ `docs/evaluation.md` records a separation gap of `0.5914` (> `0.15`) and retrieval category accuracy of `0.9333`.
4. **Qdrant parity** — intentionally deferred while `qdrant.enabled=false`; verify it before enabling Qdrant in deployment.
5. **Target-environment checks** — clean-environment installation and latency on the final VPS remain deployment checks.

## 3. External integration dependencies (outside this component)

- **Backend integration** must consume the documented API contract and persist/use similar-ticket, article, and incident fields.
- **Analyzer/Core-AI composition** must combine `analysis`, `intelligence`, and `meta`, and use the related article when producing a suggested reply.
- **Frontend, Database, DevOps, and cross-layer QA** are owned outside this component and were not assessed by this close-out.
- **Qdrant deployment** is optional and intentionally deferred; the verified default path is local Python cosine search.

---

## 4. File inventory (deliverables → repo paths)

| # | Deliverable file (flat output name) | Place at repo path |
|---|---|---|
| 1 | `infrastructure_config.json` | `ai-core/config/infrastructure_config.json` |
| 2 | `.env.example` | `ai-core/.env.example` |
| 3 | `schemas.py` | `ai-core/app/infrastructure/schemas.py` |
| 4 | `knowledge_articles.json` | `ai-core/data/knowledge_articles.json` |
| 5 | `old_tickets.json` | `ai-core/data/old_tickets.json` |
| 6 | `evaluation_set.json` | `ai-core/data/evaluation_set.json` |
| 7 | `similarity_pairs.json` | `ai-core/data/similarity_pairs.json` |
| 8 | `tickets_small.json` | `ai-core/tests/fixtures/tickets_small.json` |
| 9 | `articles_small.json` | `ai-core/tests/fixtures/articles_small.json` |
| 10 | `similarity_pairs_small.json` | `ai-core/tests/fixtures/similarity_pairs_small.json` |
| 11 | `vpn_incident_scenario.json` | `ai-core/tests/fixtures/vpn_incident_scenario.json` |
| 12 | `embedding_model.py` | `ai-core/app/infrastructure/embedding_model.py` |
| 13 | `qdrant_adapter.py` | `ai-core/app/infrastructure/qdrant_adapter.py` |
| 14 | `similarity_search.py` | `ai-core/app/infrastructure/similarity_search.py` |
| 15 | `knowledge_base.py` | `ai-core/app/infrastructure/knowledge_base.py` |
| 16 | `incident_detector.py` | `ai-core/app/infrastructure/incident_detector.py` |
| 17 | `__init__.py` | `ai-core/app/infrastructure/__init__.py` |
| 18 | `evaluation.py` | `ai-core/app/infrastructure/evaluation.py` |
| 19 | `main.py` | `ai-core/app/main.py` |
| 20 | `seed_embeddings.py` | `ai-core/scripts/seed_embeddings.py` |
| 21 | `evaluate_infrastructure.py` | `ai-core/scripts/evaluate_infrastructure.py` |
| + | `requirements.txt` | `ai-core/requirements.txt` |
| + | `README.md` | `ai-core/app/infrastructure/README.md` |
| + | `backend_integration_contract.md` | `ai-core/docs/backend_integration_contract.md` |
| (gen) | `docs/evaluation.md` | written by script |

> `ai-core/app/__init__.py` is present, so `app` is already a Python package.

---

## 5. Commit checklist

- [x] Place all files at the repo paths above; `ai-core/app/__init__.py` exists.
- [ ] `pip install -r requirements.txt` succeeds on a clean env.
- [x] `python scripts/seed_embeddings.py` builds persistent article and ticket caches under `data/.cache/`.
- [x] `uvicorn app.main:app` starts; `GET /health` and `/docs` were manually verified.
- [x] `POST /analyze-ticket` returns VPN similars, a VPN article, a high incident, and detects an existing duplicate incident.
- [x] `python scripts/evaluate_infrastructure.py` writes `docs/evaluation.md`.
- [x] `separation_gap > 0.15` (`0.5914`) in the real-model report.
- [x] Rule 6 has an automated guard test.
- [x] `.gitignore` covers `.model_cache/` and `data/.cache/`.
- [x] Automated suite passes: 22 tests.
- [ ] Confirm `latency_ms` is acceptable on the target VPS.

---

## 6. Open deployment verification items

1. **Clean environment** — install `requirements.txt` in a fresh environment and run the full test suite.
2. **Latency** — confirm per-request `latency_ms` is acceptable on the target VPS.
3. **Qdrant parity** — only required if the team later changes `qdrant.enabled` to `true`.
