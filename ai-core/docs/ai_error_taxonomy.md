# طبقه‌بندی خطاهای AI Analyzer

این سند خطاهای قابل پایش Analyzer را از خطاهای زیرساختی جدا می‌کند. متن خام تیکت و جزئیات exception نباید در پاسخ عمومی API یا لاگ سطح info ذخیره شود.

| کد | نوع خطا | نمونه فارسی | کنترل پیشنهادی |
|---|---|---|---|
| `category_incorrect` | دسته‌بندی اشتباه | تیکت «حجم ایمیل پر شده» به‌عنوان شبکه تشخیص داده شود. | ثبت اصلاح کارشناس، بررسی top labels و کالیبراسیون threshold |
| `intent_incorrect` | intent اشتباه | «درخواست VPN جدید» به‌عنوان خطای اتصال تشخیص داده شود. | بازبینی rule pack همان category و ثبت keyword مؤثر |
| `urgency_overestimated` | فوریت اغراق‌شده | عبارت «فوری نیست» به high تبدیل شود. | کنترل negation و low-priority cap |
| `urgency_underestimated` | فوریت کمتر از واقع | «کل شرکت اینترنت ندارد» medium شود. | بررسی impact label و عبارت‌های outage سازمانی |
| `sentiment_incorrect` | لحن اشتباه | پیگیری چندباره کاربر neutral تشخیص داده شود. | بررسی repetition و frustration rule pack |
| `reply_inappropriate` | پاسخ نامناسب | برای رخداد امنیتی راهنمای عمومی و بدون escalation تولید شود. | reply quality gate و escalation detector |
| `low_confidence_false_positive` | خروجی ناشناخته با اطمینان بالا | متن «کار نمی‌کند» category قطعی و confidence بالا بگیرد. | ambiguity detector و سقف confidence برای unknown/general intent |
| `model_unavailable` | مدل zero-shot در دسترس نیست | دانلود یا بارگذاری مدل شکست بخورد. | fallback قطعی rule-based، هشدار عملیاتی و عدم افشای exception |

## حداقل داده لازم برای گزارش خطا

- `ticket_id` یا شناسه ناشناس‌شده
- نسخه Analyzer
- category، intent، urgency و sentiment پیش‌بینی‌شده
- اصلاح کارشناس و نوع خطا
- decision trace فقط در محیط توسعه و بدون داده حساس
