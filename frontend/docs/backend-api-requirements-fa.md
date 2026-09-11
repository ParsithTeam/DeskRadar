# APIهای موردنیاز فرانت DeskRadar

Base URL پیشنهادی: `/api/v1`

قواعد عمومی:

- تاریخ‌ها ISO 8601 باشند؛ مثل `2026-09-01T10:30:00Z`.
- امتیازهای `confidence`، `score` و `similarity` بین `0` و `1` باشند.
- نقش، شناسه و نام کاربر از session گرفته شوند، نه body فرانت.
- پاسخ لیست‌های صفحه‌بندی‌شده:

```ts
{ items: T[]; page: number; pageSize: number; total: number }
```

## احراز هویت

| Method | Endpoint | کاربرد |
| --- | --- | --- |
| POST | `/auth/register` | ثبت‌نام کاربر عادی |
| POST | `/auth/login` | ورود |
| GET | `/auth/me` | بازیابی کاربر بعد از refresh |
| POST | `/auth/logout` | خروج |

ورودی‌ها:

```json
// register
{ "name": "حسین احمدی", "email": "user@company.ir", "password": "secret123" }

// login
{ "email": "user@company.ir", "password": "secret123" }
```

پاسخ `register`، `login` و `me`:

```json
{
  "user": {
    "id": "user-1",
    "name": "حسین احمدی",
    "email": "user@company.ir",
    "role": "user"
  }
}
```

پیشنهاد: session با cookie امن و `HttpOnly` نگه‌داری شود. ثبت‌نام همیشه نقش `user` می‌سازد. پاسخ logout می‌تواند `204` باشد.

## تیکت‌ها و تحلیل AI

| Method | Endpoint | دسترسی/کاربرد |
| --- | --- | --- |
| GET | `/tickets` | ادمین: همه تیکت‌ها؛ کاربر: فقط تیکت‌های خودش |
| POST | `/tickets` | ثبت تیکت توسط کاربر |
| GET | `/tickets/{id}` | جزئیات کامل تیکت، تحلیل و ارجاع |
| PATCH | `/tickets/{id}/status` | تغییر وضعیت توسط ادمین |
| POST | `/tickets/{id}/analyze` | تحلیل مجدد توسط ادمین |
| POST | `/tickets/{id}/analysis-feedback` | تأیید یا رد تحلیل توسط ادمین |

### نکات پاسخ

- `GET /tickets`: queryهای `q, category, urgency, status, page, pageSize` را بگیرد و `ListResponse<TicketSummary>` برگرداند. ترتیب پیش‌فرض جدیدترین اول باشد.
- `POST /tickets`: ورودی فقط `title, description, department` است. پاسخ `201` یک `TicketDetail` با `analysisStatus: "pending"`، `analysis: null` و `escalation: null` است. تحلیل باید خودکار شروع شود.
- `GET /tickets/{id}`: یک `TicketDetail` برگرداند. ارجاع و پیام‌هایش داخل فیلد `escalation` هستند؛ اگر ارجاعی نیست مقدار `null`. API جداگانه برای گرفتن ارجاع تیکت لازم نیست.
- `PATCH /tickets/{id}/status`: ورودی `{ "status": "in_progress" }` و پاسخ تیکت به‌روزشده باشد.
- `POST /tickets/{id}/analyze`: پاسخ `202` به‌شکل `{ "id": 101, "analysisStatus": "pending" }`. نتیجه با درخواست مجدد جزئیات تیکت گرفته می‌شود.
- `analysis-feedback`: ورودی `{ "value": "up" }` با مقادیر `up | down`؛ پاسخ موفق `204`.

ورودی ثبت تیکت:

```json
{
  "title": "اتصال VPN برقرار نمی‌شود",
  "description": "از صبح خطای احراز هویت می‌بینم.",
  "department": "واحد فروش"
}
```

وضعیت‌های تیکت:

```text
open | in_progress | escalated | resolved | closed
```

## ارجاع به کارشناس و گفتگو

| Method | Endpoint | دسترسی/کاربرد |
| --- | --- | --- |
| POST | `/tickets/{id}/escalations` | ارجاع تیکت توسط صاحب آن |
| GET | `/escalations` | اینباکس ارجاع‌های ادمین |
| GET | `/escalations/{id}` | جزئیات پرونده، تیکت و پیام‌ها |
| POST | `/escalations/{id}/messages` | ارسال پیام توسط صاحب تیکت یا ادمین |
| PATCH | `/escalations/{id}/status` | پذیرش یا بستن توسط ادمین |

### نکات پاسخ

- ساخت ارجاع ورودی `{ "reason": "..." }` و خروجی `Escalation` دارد. هم‌زمان وضعیت تیکت `escalated` شود، reason اولین پیام باشد و برای ادمین هشدار ساخته شود.
- اگر همان تیکت ارجاع `waiting` یا `active` دارد، ارجاع جدید ساخته نشود و همان قبلی برگردد.
- `GET /escalations`: queryهای `q, status, page, pageSize` و پاسخ `ListResponse<EscalationListItem>`. خلاصه تیکت و آخرین پیام داخل هر آیتم باشد تا درخواست اضافه لازم نشود.
- `GET /escalations/{id}`: پاسخ `{ escalation: Escalation, ticket: TicketSummary }`.
- ارسال پیام ورودی `{ "text": "..." }` و خروجی `Escalation` به‌روزشده دارد. اولین پاسخ ادمین، پرونده را `active` و ادمین را مسئول کند.
- تغییر وضعیت ورودی `{ "status": "active" }` و خروجی `Escalation` به‌روزشده دارد. مقادیر مجاز ادمین `active | resolved` هستند.
- با `resolved` شدن ارجاع، تیکت مرتبط هم در همان transaction به `resolved` تغییر کند. پرونده بسته پیام جدید نپذیرد.

## رخدادها

| Method | Endpoint | دسترسی/کاربرد |
| --- | --- | --- |
| GET | `/incidents` | لیست رخدادها برای ادمین |
| GET | `/incidents/{id}` | جزئیات رخداد و تیکت‌های مشابه |
| PATCH | `/incidents/{id}/status` | تأیید یا رفع رخداد توسط ادمین |

- لیست queryهای `q, status, page, pageSize` و پاسخ `ListResponse<IncidentSummary>` دارد.
- جزئیات یک `Incident` کامل همراه تیکت‌های مرتبط و امتیاز `similarity` برمی‌گرداند.
- تغییر وضعیت ورودی `{ "status": "confirmed" }` و خروجی رخداد به‌روزشده دارد. مقادیر: `candidate | confirmed | resolved | dismissed`. وضعیت `dismissed` یعنی ادمین رخداد پیشنهادی را رد کرده است. هنگام رفع، سرور `resolvedAt` را ثبت کند.

## پایگاه دانش

| Method | Endpoint | دسترسی/کاربرد |
| --- | --- | --- |
| GET | `/knowledge-articles` | لیست و جستجو برای همه کاربران |
| GET | `/knowledge-articles/{id}` | جزئیات کامل مقاله |
| POST | `/knowledge-articles` | ساخت مقاله توسط ادمین |

- لیست queryهای `q, category, page, pageSize` و پاسخ `ListResponse<KnowledgeArticleSummary>` دارد؛ `content` فقط در جزئیات لازم است.
- ساخت مقاله ورودی `title, summary, category, tags, content` و پاسخ `201` با مدل کامل مقاله دارد. `author` و `updatedAt` را سرور تعیین کند.

## هشدارها

| Method | Endpoint | دسترسی/کاربرد |
| --- | --- | --- |
| GET | `/alerts` | لیست هشدارها و وضعیت تخصیص آن‌ها برای ادمین |
| POST | `/alerts/{id}/read` | خواندن و تخصیص هشدار به اولین ادمین |
| WS | `/ws/alerts` | دریافت زنده هشدار جدید |

- به‌خاطر polling فعلی، `GET /alerts` مستقیماً آخرین Alertها را به‌شکل `Alert[]` برگرداند، نه پاسخ صفحه‌بندی‌شده. پاسخ باید موارد خوانده‌شده را هم داشته باشد تا assignment بین ادمین‌ها sync شود.
- `POST /alerts/{id}/read` body ندارد؛ ادمین از session مشخص می‌شود. اولین درخواست باید به‌صورت اتمیک `read=true` کند و `assignedAdminId/assignedAdminName` را ثبت کند. درخواست ادمین‌های بعدی نباید مسئول را تغییر دهد و همان Alert فعلی را برگرداند.
- بعد از خوانده‌شدن، Alert به‌روزشده برای همه ادمین‌های متصل broadcast شود تا برای آن‌ها نیز خوانده‌شده و همراه نام مسئول نمایش داده شود.
- هر پیام WebSocket دقیقاً یک `Alert` جدید یا به‌روزشده باشد. در صورت قطع اتصال، فرانت هر ۱۵ ثانیه `GET /alerts` را صدا می‌زند.

## داشبورد

| Method | Endpoint | کاربرد |
| --- | --- | --- |
| GET | `/dashboard/summary` | آمار خلاصه بر اساس نقش |

`dashboard/summary` لازم است تا برای نمایش آمار، تمام صفحات لیست‌ها دانلود نشوند.

پاسخ ادمین:

```ts
{
  openTickets: number;
  urgentTickets: number;
  activeIncidents: number;
  waitingEscalations: number;
  categoryCounts: Record<TicketCategory, number>;
  recentAlerts: Alert[];
}
```

پاسخ کاربر:

```ts
{
  openTickets: number;
  resolvedTickets: number;
  activeEscalations: number;
  recentTickets: TicketSummary[];
}
```

## مدل‌های مرجع

```ts
type Role = "admin" | "user";
type TicketCategory = "vpn" | "email" | "network" | "printer" | "account";
type Urgency = "low" | "medium" | "high" | "critical";
type TicketStatus = "open" | "in_progress" | "escalated" | "resolved" | "closed";
type AnalysisStatus = "pending" | "complete" | "failed";
type EscalationStatus = "waiting" | "active" | "resolved";
type IncidentStatus = "candidate" | "confirmed" | "resolved" | "dismissed";

interface TicketSummary {
  id: number;
  title: string;
  department: string;
  requesterId: string;
  requesterName: string;
  category: TicketCategory;
  categoryLabelFa: string;
  urgency: Urgency;
  status: TicketStatus;
  analysisStatus: AnalysisStatus;
  confidence: number;
  createdAt: string;
  updatedAt: string;
}

interface TicketDetail extends TicketSummary {
  description: string;
  analysis: TicketAnalysis | null;
  escalation: Escalation | null;
}

interface TicketAnalysis {
  category: TicketCategory;
  categoryLabelFa: string;
  intentLabelFa: string;
  urgency: Urgency;
  confidence: number;
  summaryFa: string;
  suggestedReplyFa: string;
  reasonsFa: string[];
  similarTickets: Array<{ id: number; title: string; score: number }>;
  relatedArticle: { id: number; title: string; score: number } | null;
  possibleIncident: boolean;
}

interface EscalationMessage {
  id: string;
  senderId: string;
  senderName: string;
  senderRole: Role;
  text: string;
  createdAt: string;
}

interface Escalation {
  id: string;
  ticketId: number;
  requesterId: string;
  requesterName: string;
  reason: string;
  status: EscalationStatus;
  assignedAdminId?: string;
  assignedAdminName?: string;
  createdAt: string;
  updatedAt: string;
  messages: EscalationMessage[];
}

interface EscalationListItem extends Omit<Escalation, "messages"> {
  ticket: Pick<TicketSummary, "id" | "title" | "status" | "urgency">;
  lastMessage: EscalationMessage;
}

interface Incident {
  id: number;
  title: string;
  description: string;
  category: TicketCategory;
  categoryLabelFa: string;
  severity: "low" | "medium" | "high" | "critical";
  status: IncidentStatus;
  detectedReason: string;
  createdAt: string;
  resolvedAt?: string;
  tickets: Array<{ ticketId: number; title: string; similarity: number }>;
}

type IncidentSummary = Omit<Incident, "tickets"> & { ticketCount: number };

interface KnowledgeArticle {
  id: number;
  title: string;
  summary: string;
  category: TicketCategory;
  categoryLabelFa: string;
  tags: string[];
  content: string;
  updatedAt: string;
  author: string;
}

type KnowledgeArticleSummary = Omit<KnowledgeArticle, "content">;

interface Alert {
  id: string;
  title: string;
  message: string;
  severity: "low" | "medium" | "high" | "critical";
  type: "incident" | "ticket" | "escalation";
  createdAt: string;
  read: boolean;
  assignedAdminId?: string;
  assignedAdminName?: string;
  href?: string;
}
```

## قوانین دسترسی

- کاربر فقط تیکت‌ها و ارجاع‌های خودش را ببیند.
- فقط صاحب تیکت بتواند آن را ارجاع دهد یا در گفتگوی آن پیام بفرستد.
- فقط ادمین وضعیت تیکت، ارجاع و رخداد را تغییر دهد.
- فقط ادمین مقاله بسازد و هشدارها را ببیند.
- امنیت در بک‌اند enforce شود و به مخفی‌بودن صفحات فرانت وابسته نباشد.
