# ServiceDesk Radar — Unified AI Core API Contract

This document specifies the unified HTTP contract between **Backend** and **AI Core**.

---

## 1. Overview & Service Address

- **Base URL:** `http://127.0.0.1:8001`
- **Swagger Documentation:** `http://127.0.0.1:8001/docs`
- **Primary Endpoint:** `POST /analyze`
- **Readiness Check:** `GET /health`

The Backend communicates with AI Core through **one single endpoint (`POST /analyze`)** to receive both Persian NLP text analysis (`analysis`) and semantic vector intelligence (`intelligence`).

---

## 2. Primary Endpoint: `POST /analyze`

### Request Payload (`UnifiedAnalyzeRequest`)

```json
{
  "ticket_id": 101,
  "title": "VPN وصل نمی‌شود",
  "description": "خطای احراز هویت نمایش داده می‌شود و نیم ساعت دیگر جلسه کاری دارم.",
  "category": "vpn",
  "old_tickets": [
    {
      "ticket_id": 18,
      "title": "خطا در اتصال به VPN",
      "description": "وی‌پی‌ان وصل نمیشه",
      "category": "vpn",
      "status": "open"
    },
    {
      "ticket_id": 22,
      "title": "مشکل احراز هویت شبکه",
      "description": "خطای login در وی پی ان",
      "category": "vpn",
      "status": "open"
    },
    {
      "ticket_id": 35,
      "title": "قطعی وی پی ان",
      "description": "دسترسی به سرور ندارم",
      "category": "vpn",
      "status": "open"
    },
    {
      "ticket_id": 41,
      "title": "ارور دسترسی راه دور",
      "description": "vpn خطا میده",
      "category": "vpn",
      "status": "open"
    }
  ],
  "open_incidents": [
    {
      "incident_id": 7,
      "category": "vpn",
      "matched_ticket_ids": [18, 22, 35]
    }
  ],
  "debug": false
}
```

#### Field Descriptions:
- `ticket_id` *(integer, optional)*: Unique ID of the incoming ticket.
- `title` *(string, required)*: Ticket title/subject.
- `description` *(string, optional)*: Full ticket body/description.
- `category` *(string, optional)*: Category hint if already known (e.g. `vpn`, `email`, `network`, `printer`, `account`, `hardware`, `software`, `permission`). If omitted, Analyzer detects it automatically.
- `old_tickets` *(array of objects, optional)*: Pool of active/open tickets from the DB for semantic similarity search. (Tickets with status `closed` or `deleted` are ignored).
- `open_incidents` *(array of objects, optional)*: List of currently open incidents in the DB for deduplication.

---

### Response Payload (`UnifiedAnalyzeResponse`)

```json
{
  "ticket_id": 101,
  "status": "completed",
  "analysis": {
    "category": "vpn",
    "category_label_fa": "اتصال VPN و شبکه راه دور",
    "category_score": 0.94,
    "category_source": "zero_shot_model",
    "intent": "vpn_connection_issue",
    "intent_label_fa": "مشکل در برقراری ارتباط با VPN",
    "intent_score": 0.85,
    "urgency": "high",
    "urgency_score": 75,
    "impact_label": "individual",
    "impact_label_fa": "فردی",
    "sentiment": "negative",
    "frustration_score": 60,
    "summary_fa": "کاربر در اتصال به VPN با خطای احراز هویت مواجه شده و اعلام کرده که جلسه کاری در پیش دارد.",
    "suggested_reply_fa": "همکار گرامی، سلام.\nدرخواست شما مبنی بر مشکل در اتصال به VPN دریافت شد. لطفاً ابتدا اتصال اینترنت خود را بررسی نموده و از صحت نام کاربری و رمز عبور اطمینان حاصل فرمایید. در صورت تداوم مشکل، اسکرین‌شات پیام خطا را ارسال نمایید.\nبا احترام، تیم پشتیبانی فناوری اطلاعات",
    "reply_tone": "empathic_professional",
    "confidence": 0.91,
    "confidence_percent": 91,
    "reasons_fa": [
      "دسته‌بندی با مدل هوش مصنوعی Zero-Shot شناسایی شد.",
      "به دلیل اشاره به جلسه کاری، سطح فوریت بالا تعیین شد."
    ],
    "should_escalate": false,
    "escalation_reason_fa": "نیاز به ارجاع فوری به سطح بالاتر ندارد.",
    "needs_more_info": false,
    "clarification_question_fa": null,
    "ui_labels": {
      "category": "اتصال VPN و شبکه راه دور",
      "urgency": "بالا",
      "sentiment": "ناراضی / نگران"
    }
  },
  "intelligence": {
    "similar_tickets": [
      {
        "ticket_id": 18,
        "similarity": 0.9124,
        "match_level": "very_similar",
        "title": "خطا در اتصال به VPN",
        "category": "vpn"
      },
      {
        "ticket_id": 22,
        "similarity": 0.8841,
        "match_level": "very_similar",
        "title": "مشکل احراز هویت شبکه",
        "category": "vpn"
      },
      {
        "ticket_id": 35,
        "similarity": 0.8320,
        "match_level": "similar",
        "title": "قطعی وی پی ان",
        "category": "vpn"
      },
      {
        "ticket_id": 41,
        "similarity": 0.8115,
        "match_level": "similar",
        "title": "ارور دسترسی راه دور",
        "category": "vpn"
      }
    ],
    "related_article": {
      "article_id": 1,
      "title": "راهنمای رفع خطای احراز هویت VPN",
      "score": 0.8850,
      "category": "vpn",
      "tags": ["vpn", "authentication", "mfa"]
    },
    "incident": {
      "possible_incident": true,
      "severity": "high",
      "fa_title_incident": "رخداد احتمالی در سرویس VPN",
      "fa_reason_incident": "۴ تیکت مشابه با میانگین شباهت ۰.۸۶ در دسته VPN شناسایی شد.",
      "matched_ticket_ids": [18, 22, 35, 41],
      "avg_similarity_score": 0.86,
      "is_duplicate": true,
      "duplicate_incident_id": 7
    },
    "embedding_model_version": "multilingual-MiniLM-L12-v2-v1",
    "latency_ms": 112.4,
    "error": null
  },
  "meta": {
    "status": "completed",
    "embedding_model_version": "multilingual-MiniLM-L12-v2-v1",
    "analyzer_model_version": "1.0.0",
    "latency_ms": 284.5,
    "analyzed_at": "2026-08-24T13:40:00.000Z",
    "error": null
  }
}
```

---

## 3. Backend Integration Responsibilities

1. **Analysis Storage:** Store `analysis` (category, urgency, summary, suggested reply, etc.) directly into `ticket_analysis` table.
2. **Intelligence Storage:** Store `intelligence.similar_tickets` and `intelligence.related_article` with the ticket record.
3. **Incident Management:**
   - When `intelligence.incident.possible_incident == false`: Do not create an incident.
   - When `is_duplicate == true`: Update the existing incident record (`duplicate_incident_id`), appending the new `matched_ticket_ids`.
   - When `is_duplicate == false` and `possible_incident == true`: Create a new `Incident` in DB with `matched_ticket_ids`.
4. **Resilience & Degraded Mode:**
   - If `status == "completed"`: Full success.
   - If `status == "partial"`: Save whatever succeeded (e.g. analysis succeeded even if similarity failed).
   - If transport failure / HTTP timeout: Set analysis status to `"failed"`.

---

## 4. Standalone Sub-Endpoints (Optional / Diagnostics)

- `POST /analyzer/analyze`: Runs Analyzer NLP only.
- `POST /analyze-ticket`: Runs Infrastructure Semantic Intelligence only.
- `GET /health`: Readiness status of all models and vector indexes.
