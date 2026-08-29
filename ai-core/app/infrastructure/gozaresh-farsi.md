<div dir="rtl" align="right">

# گزارش پروژه — هوش مصنوعی زیرساخت (AI Infrastructure)

**پروژه:** ServiceDesk Radar — داشبورد هوشمند مدیریت تیکت‌های پشتیبانی IT با هسته‌ی AI فارسی‌محور
**شاخه (Branch):** `ai-infrastructure`
**دامنه‌ی کاری این گزارش:** `ai-core/app/infrastructure/` به‌همراه config، data، docs، scripts، tests و ورودی FastAPI
**وضعیت:** حالت پیش‌فرض Python-cosine با Qdrant خاموش تکمیل و تست شده است؛ ارزیابی با **مدل واقعی** ثبت شده و **۲۲ تست واحد/یکپارچه** پاس می‌شوند.

---

## ۱) این بخش چه کاری انجام می‌دهد؟

این کامپوننت، «روابط پنهان» بین تیکت‌ها و مقاله‌ها را پیدا می‌کند؛ چیزی که تحلیل تک‌تیکتی نمی‌تواند ببیند. با دریافت یک تیکت جدید به‌همراه مجموعه‌ی تیکت‌های قبلی، خروجی زیر (بلوک `intelligence`) را تولید می‌کند:

- **پنج تیکت مشابه برتر** همراه با امتیاز شباهت و سطح تطبیق (`similar` یا `very_similar`).
- **مرتبط‌ترین مقاله‌ی راهنما** (یا `null` اگر امتیاز پایین‌تر از حد آستانه باشد).
- **تشخیص رخداد احتمالی (Incident)**: اینکه آیا چند تیکت مشابه در یک دسته، نشانه‌ی یک مشکل گسترده هستند؛ به‌همراه شدت، عنوان و دلیل فارسی، شناسه‌های مرتبط، `is_duplicate` و `duplicate_incident_id`.
- **اطلاعات همراه**: نسخه‌ی مدل embedding، زمان پردازش (ms)، و فیلد `error` که در موفقیت `null` است.

این بخش **دسته‌بندی/فوریت/پاسخ تولید نمی‌کند**؛ آن وظیفه‌ی Analyzer AI است. این دو کاملاً مستقل‌اند و ترکیب خروجی‌ها در Backend انجام می‌شود.

---

## ۲) جایگاه در سیستم

پروژه چهار بخش مستقل دارد:

| بخش | مسئولیت |
|---|---|
| Frontend (Next.js) | داشبورد: تیکت‌ها، رخدادها، مقاله‌ها، هشدارها |
| Backend (FastAPI) | داده، دیتابیس، Import CSV، WebSocket، هماهنگ‌سازی |
| Analyzer AI | تحلیل متن فارسی: category، intent، urgency، sentiment، summary، reply |
| **AI Infrastructure** (این بخش) | **embedding، شباهت، بازیابی دانش، تشخیص رخداد** |

Backend از طریق HTTP این سرویس را صدا می‌زند، تیکت جدید و **مجموعه‌ی تیکت‌های قبلی** را می‌فرستد و خروجی را ذخیره می‌کند.

---

## ۳) معماری

```
infrastructure_config.json  (تنها منبع حقیقت برای آستانه‌ها)
        │
        ▼
EmbeddingModel  (singleton، فقط یک‌بار در startup لود می‌شود)
        │                              │
        ▼                              ▼
similarity_search.py            knowledge_base.py
 (+ qdrant_adapter اختیاری)      (+ qdrant_adapter اختیاری)
        │                              │
        └──────────────┬───────────────┘
                       ▼
              incident_detector.py   (لیست SimilarTicket را پارامتری می‌گیرد؛ هرگز similarity_search را صدا نمی‌زند)
                       │
                       ▼
              __init__.py  →  run_infrastructure() کل خط لوله را هماهنگ می‌کند
                       │
                       ▼
              InfrastructureResult  →  app/main.py (FastAPI)

evaluation.py — فقط آفلاین؛ از بقیه import می‌کند ولی هیچ ماژولی آن را import نمی‌کند.
```


- **مدل embedding:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (پشتیبانی بومی از فارسی و متن ترکیبی فارسی/انگلیسی).
- **ذخیره‌سازی بردار:** پیش‌فرض و همیشه‌دردسترس، شباهت کسینوسی خالص با Python است. **Qdrant اختیاری** و کاملاً ایزوله است.
- **cache پایدار تیکت‌ها:** بردار هر تیکت با `ticket_id + text_hash + model_version` ذخیره می‌شود و پس از restart فقط در صورت تغییر متن یا مدل دوباره ساخته می‌شود.

---

## ۴) اجزای پیاده‌سازی‌شده (گام به گام)

| گام | فایل | کار انجام‌شده |
|---|---|---|
| ۱ | `config/infrastructure_config.json` | تنها منبع آستانه‌ها و مسیر cacheهای مقاله و تیکت؛ ساختار آن هنگام startup با Pydantic اعتبارسنجی می‌شود. |
| ۲ | `.env.example` | متغیرهای محیطی اجرا؛ فایل `.env` خودکار خوانده می‌شود و process environment اولویت دارد. |
| ۳ | `app/infrastructure/schemas.py` | مدل‌های ورودی/خروجی، `OpenIncidentRecord`، cacheها، health و config. |
| ۴ | `data/knowledge_articles.json` | ۱۱ مقاله‌ی فارسی پوشش‌دهنده‌ی vpn، email، printer، network، account. |
| ۵ | `data/old_tickets.json` | ۵۵ تیکت نمونه با خوشه‌ی VPN برای سناریوی رخداد و ترکیب وضعیت‌ها. |
| ۶ | `data/evaluation_set.json` | ۶۰ تیکت برچسب‌خورده (۱۲ تیکت در هر دسته). |
| ۷ | `data/similarity_pairs.json` | ۲۳ جفت مشابه + ۲۲ جفت غیرمشابه به‌عنوان ground truth. |
| ۸ تا ۱۱ | `tests/fixtures/*.json` | داده‌های کوچک و قطعی برای تست‌ها (۵ VPN + ۵ printer، ۵ مقاله، جفت‌ها، سناریوی رخداد VPN). |
| ۱۲ | `embedding_model.py` | کلاس singleton مدل، `encode()`، `build_ticket_text()`، خطای `ModelNotReadyError`. |
| ۱۳ | `qdrant_adapter.py` | اتصال اختیاری Qdrant: health_check، ensure_collections، upsert، search + پرچم availability. |
| ۱۴ | `similarity_search.py` | تابع `find_similar_tickets` با حذف self-match، فیلتر بسته/حذف‌شده، آستانه‌های config. |
| ۱۵ | `knowledge_base.py` | بارگذاری مقاله، ساخت embedding با cache (بر اساس model_version و text_hash)، و `find_related_article`. |
| ۱۶ | `incident_detector.py` | تابع `detect_incident_candidate` با شدت medium/high، عنوان و دلیل فارسی، dedup مبتنی بر اشتراک خوشه و `duplicate_incident_id`؛ برچسب فارسی برای ۷ دسته (شامل نرم‌افزار/سخت‌افزار). |
| ۱۷ | `__init__.py` | هماهنگ‌کننده، cache پایدار تیکت‌ها، بارگذاری `.env` و API عمومی. |
| ۱۸ | `evaluation.py` | ارزیابی آفلاین: کیفیت شباهت، جاروی آستانه، و دقت دسته‌بندیِ retrieval (نه Analyzer). |
| ۱۹ | `app/main.py` | اپ FastAPI: `/health` و `/analyze-ticket`. |
| ۲۰ | `scripts/seed_embeddings.py` | ساخت cache مقاله‌ها. |
| ۲۱ | `scripts/evaluate_infrastructure.py` | اجرای ارزیابی و تولید `docs/evaluation.md`. |

علاوه بر این‌ها: `requirements.txt`، `README.md`، `.gitignore`، `app/__init__.py` و مجموعه‌ی تست (`tests/`).

---

## ۵) خط لوله‌ی پردازش هر تیکت (per request)

تابع `run_infrastructure()` این مراحل ثابت را اجرا می‌کند:

1. ساخت **متن استاندارد** از عنوان + توضیح (+ دسته‌ی اختیاری).
2. تبدیل به **بردار** با مدل؛ embedding تیکت‌های قبلی از cache پایدار بازاستفاده می‌شود.
3. **یافتن تیکت‌های مشابه**: شباهت کسینوسی، حذف خودتطبیقی، فیلتر تیکت‌های `closed`/`deleted`، نگه‌داشتن موارد بالای آستانه‌ی شباهت، مرتب‌سازی و محدودسازی به `top_k`.
4. **یافتن مقاله‌ی مرتبط** (نزدیک‌ترین مقاله ≥ حداقل امتیاز، در غیر این‌صورت `null`).
5. **تشخیص رخداد**: تعیین medium/high و بررسی dedup با اشتراک `matched_ticket_ids` در `open_incidents`؛ در حالت تکراری، `duplicate_incident_id` برمی‌گردد.
6. **مونتاژ نتیجه**.

هر مرحله ایزوله است؛ خطای یک مرحله نتایج مراحل قبل را از بین نمی‌برد و در فیلد `error` گزارش می‌شود.

> **قرارداد مهم با Backend:** در حالت پیش‌فرض، جست‌وجو فقط روی `old_tickets` همان درخواست انجام می‌شود. Backend برای dedup نیز باید `open_incidents` شامل `incident_id`، category و `matched_ticket_ids` را بفرستد. قرارداد کامل در `docs/backend_integration_contract.md` است.

---

## ۶) ارزیابی (Evaluation) — نتایج واقعی

اسکریپت `scripts/evaluate_infrastructure.py` با **مدل واقعی** اجرا شد و `docs/evaluation.md` را تولید کرد. نتایج:

**کیفیت شباهت**

| سنجه | مقدار |
|---|---|
| تعداد جفت‌ها | ۴۵ |
| میانگین امتیاز جفت‌های مشابه | ۰.۷۸ |
| میانگین امتیاز جفت‌های غیرمشابه | ۰.۱۹ |
| فاصله‌ی جداسازی (هدف > ۰.۱۵) | **۰.۵۹** ✅ |
| نرخ قبولی (در آستانه‌ی ۰.۷۰) | ۰.۸۹ |

**دقت دسته‌بندی retrieval (نه Analyzer):** کلی **۹۳٪** (۵۶ از ۶۰). به‌تفکیک: email/network/printer = ۱۰۰٪، vpn ≈ ۹۲٪، account = ۷۵٪.

**آستانه‌ی عملیاتی منتخب: `۰.۷۰`.** از میان مقادیر پیشنهادی Taskbook §9.8 ({۰.۷۰، ۰.۷۵، ۰.۷۸، ۰.۸۲})، مقدار ۰.۷۰ بالاترین نرخ قبولی (۰.۸۹) را دارد در حالی‌که فاصله‌ی جداسازی همچنان ۰.۵۹ (> ۰.۱۵) می‌ماند. اعداد کمتری که اسکریپت چاپ می‌کند (۰.۴۸ = میانهٔ امتیازها، ۰.۶۵ = argmax جارو) صرفاً heuristic بدون قید هستند؛ ما نقطه‌ی عملیاتی را روی یک مقدار مصرّح در Taskbook تثبیت کردیم تا precision حفظ شود.

---

## ۷) نگاشت خروجی به بلوک استاندارد `intelligence` (Taskbook §2.3)

خروجی این سرویس **سوپرستِ** schema §2.3 است (فیلد بیشتری دارد). Backend هنگام ترکیب، این نگاشت را اعمال می‌کند:

| فیلد در §2.3 `intelligence` | منبع در `InfrastructureResult` |
|---|---|
| `similar_tickets[].ticket_id`, `.similarity` | `similar_tickets[]` (به‌علاوه‌ی `match_level`، `title`، `category`) |
| `related_article` | `related_article` (به‌علاوه‌ی `category`، `tags`؛ زیر کف امتیاز = `null`) |
| `possible_incident` | `incident.possible_incident` |
| `incident_title_fa` | `incident.fa_title_incident` |

> این سرویس یک شیء **incident غنی‌تر** برمی‌گرداند (`severity`، `fa_reason_incident`، `matched_ticket_ids`، `avg_similarity_score`، `is_duplicate` و `duplicate_incident_id`). Backend دو فیلد §2.3 را از آن بیرون می‌کشد و بقیه را می‌تواند ذخیره کند. برای dedup، Backend باید `open_incidents` شامل شناسهٔ incident و تیکت‌های خوشه را بفرستد؛ قرارداد کامل در `docs/backend_integration_contract.md` است.

---

## ۸) قوانین طراحی (که همیشه رعایت شده‌اند)

1. `run_infrastructure()` هرگز exception پرتاب نمی‌کند؛ خطاها در فیلد `error` می‌آیند.
2. `incident_detector.py` هرگز `similarity_search.py` را import نمی‌کند.
3. مدل هرگز هنگام import لود نمی‌شود؛ فقط در فراخوانی صریح `load()`.
4. همه‌ی آستانه‌های عددی از `infrastructure_config.json` می‌آیند.
5. زیرساخت هرگز از `analyzer/` import نمی‌کند.
6. `evaluation.py` فقط آفلاین است و در مسیر زنده استفاده نمی‌شود (با تست `test_ci_rules.py` تضمین شده).
7. هر فایل داده با Pydantic اعتبارسنجی می‌شود؛ رکورد نامعتبر با WARNING رد می‌شود، نه crash.
8. سرویس بدون Qdrant هم کار می‌کند؛ پیش‌فرض، کسینوسی Python است.

---

## ۹) تست‌ها

مجموعه‌ی تست در `tests/` شامل fixtureهای قطعی و **۲۲ تست** است که **همگی پاس شدند**:

- `test_embedding_model.py` — فرمت `build_ticket_text`، خطای `ModelNotReadyError`، نگهبان `ENVIRONMENT=test`.
- `test_similarity_search.py` — «فقط VPN در پنج نتیجه‌ی برتر»، حذف self-match، فیلتر بسته/حذف‌شده، آستانه.
- `test_knowledge_base.py` — مقاله‌ی VPN با امتیاز ≥ ۰.۷۰، نامرتبط → None، بارگذاری از cache در startup دوم (بدون محاسبه‌ی مجدد).
- `test_incident_detector.py` — ۴ تیکت → high، ۲–۳ → medium، ۱ → بدون رخداد، رشته‌های فارسی، و dedup فقط با اشتراک خوشه.
- `test_pipeline.py` — یکپارچه: initialize → ok، سناریوی رخداد VPN → شدت high و مقاله‌ی VPN و `error=None`.
- `test_ci_rules.py` — نگهبان قانون ۶ (عدم import شدن `evaluation.py` در مسیر زنده).
- `test_ticket_embedding_cache.py`، `test_persian_pipeline.py`، `test_api_resilience.py`، `test_config_environment.py` و `test_evaluation.py` — persistence cache، سناریوی فارسی، تاب‌آوری API، config/environment و metricهای evaluation.

تست‌ها از یک «مدل ساختگی» استفاده می‌کنند، پس برای اجرا نیازی به دانلود مدل واقعی نیست (`pytest`).

---

## ۱۰) نحوه‌ی اجرا

```powershell
Set-Location "C:\Users\Victus 16\DeskRadar\ai-core"

# نصب وابستگی‌ها و ساخت فایل محیط
& "..\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }

# ساخت cache مقاله‌ها
& "..\.venv\Scripts\python.exe" scripts\seed_embeddings.py

# اجرای سرویس؛ Swagger در http://127.0.0.1:8001/docs
& "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001

# ارزیابی واقعی و تولید docs/evaluation.md
& "..\.venv\Scripts\python.exe" scripts\evaluate_infrastructure.py

# اجرای تست‌ها در مسیر موقت برای ایزوله‌ماندن cache تست
Push-Location C:\tmp
& "C:\Users\Victus 16\DeskRadar\.venv\Scripts\python.exe" -m pytest `
  "C:\Users\Victus 16\DeskRadar\ai-core\tests" -q -p no:cacheprovider
Pop-Location
```

</div>
