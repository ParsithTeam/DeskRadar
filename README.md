# DeskRadar

DeskRadar یک سامانه Service Desk با هسته تحلیل فارسی است. بخش `ai-core` متن تیکت را به category، intent، urgency، sentiment، summary، suggested reply، confidence و دلایل قابل نمایش تبدیل می‌کند و در صورت نبود مدل zero-shot به rule fallback قطعی برمی‌گردد.

## اجرای AI Core

```powershell
cd ai-core
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Swagger در `http://localhost:8001/docs` و endpoint اصلی در `POST /analyzer/analyze` در دسترس است. برای جلوگیری از preload مدل در محیط توسعه، `ANALYZER_PRELOAD_MODEL=false` تنظیم شود.

## تست و کنترل کیفیت

```powershell
cd ai-core
python -m unittest discover -s tests -v
python -m compileall -q app
```

جزئیات خطاهای تحلیلی در `ai-core/docs/ai_error_taxonomy.md` ثبت شده است.
