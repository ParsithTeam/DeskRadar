import type {
  Alert,
  AppSnapshot,
  Incident,
  KnowledgeArticle,
  Ticket,
  TicketAnalysis,
  TicketCategory,
} from "@/types";

export const categoryLabels: Record<TicketCategory, string> = {
  vpn: "مشکل VPN",
  email: "سرویس ایمیل",
  network: "شبکه و اینترنت",
  printer: "پرینتر و سخت‌افزار",
  account: "حساب و دسترسی",
};

export const seedArticles: KnowledgeArticle[] = [
  {
    id: 12,
    title: "راهنمای رفع خطای احراز هویت VPN سازمان",
    summary:
      "مراحل بررسی نام کاربری، پاک‌سازی نشست قبلی و اتصال مجدد به سرویس دسترسی از راه دور.",
    category: "vpn",
    categoryLabelFa: categoryLabels.vpn,
    tags: ["VPN", "احراز هویت", "دسترسی از راه دور"],
    content:
      "## نشانه‌های خطا\n\nاگر پس از وارد کردن رمز عبور پیام «Authentication failed» می‌بینید، ابتدا از درست بودن نام دامنه مطمئن شوید.\n\n## مراحل پیشنهادی\n\n1. اتصال VPN را کامل قطع کنید.\n2. پنج دقیقه صبر کنید تا نشست قبلی بسته شود.\n3. نام کاربری را به‌شکل `domain\\\\username` وارد کنید.\n4. اگر رمز عبور اخیراً تغییر کرده، سیستم را یک‌بار Restart کنید.\n\n## چه زمانی با پشتیبانی تماس بگیریم؟\n\nاگر چند کاربر هم‌زمان همین خطا را دارند، احتمال رخداد عمومی وجود دارد و لازم است تیکت ثبت شود.",
    updatedAt: "۱۴۰۵/۰۳/۱۰",
    author: "تیم زیرساخت",
  },
  {
    id: 13,
    title: "همگام‌سازی Outlook بعد از تغییر رمز عبور",
    summary:
      "روش حذف اطلاعات ورود قبلی و برقراری دوباره ارتباط Outlook با حساب سازمانی.",
    category: "email",
    categoryLabelFa: categoryLabels.email,
    tags: ["Outlook", "ایمیل", "رمز عبور"],
    content:
      "## علت رایج\n\nبعد از تغییر رمز عبور، Credential قدیمی ممکن است در سیستم باقی بماند.\n\n## راه‌حل\n\n1. Outlook را ببندید.\n2. در Credential Manager ورودی مربوط به Office را حذف کنید.\n3. Outlook را باز کنید و رمز جدید را وارد کنید.\n4. تا پایان همگام‌سازی از بستن برنامه خودداری کنید.",
    updatedAt: "۱۴۰۵/۰۳/۰۹",
    author: "تیم سرویس‌های سازمانی",
  },
  {
    id: 14,
    title: "بررسی پرینتر آفلاین در شبکه داخلی",
    summary:
      "چک‌لیست کوتاه برای بررسی برق، کابل شبکه، صف چاپ و نصب دوباره پرینتر.",
    category: "printer",
    categoryLabelFa: categoryLabels.printer,
    tags: ["پرینتر", "شبکه", "صف چاپ"],
    content:
      "## بررسی اولیه\n\nچراغ شبکه و وضعیت کاغذ دستگاه را بررسی کنید. سپس یک‌بار صف چاپ را پاک کنید.\n\n## نصب دوباره\n\nدر Settings وارد Printers شوید، دستگاه را Remove کنید و با آدرس ثبت‌شده در واحد IT دوباره اضافه کنید.",
    updatedAt: "۱۴۰۵/۰۳/۰۷",
    author: "پشتیبانی سخت‌افزار",
  },
  {
    id: 15,
    title: "درخواست استاندارد دسترسی به مخازن GitLab",
    summary:
      "اطلاعات لازم برای درخواست دسترسی و تفاوت سطح‌های Guest، Reporter و Developer.",
    category: "account",
    categoryLabelFa: categoryLabels.account,
    tags: ["GitLab", "دسترسی", "DevOps"],
    content:
      "## اطلاعات مورد نیاز\n\nنام پروژه، نام کاربری GitLab، سطح دسترسی و تأیید مدیر مستقیم را در تیکت بنویسید.\n\n## سطح پیشنهادی\n\nبرای توسعه کد معمولاً سطح Developer کافی است. سطح Maintainer فقط با تأیید مالک سرویس داده می‌شود.",
    updatedAt: "۱۴۰۵/۰۳/۰۵",
    author: "تیم DevOps",
  },
  {
    id: 16,
    title: "رفع قطعی‌های کوتاه شبکه بی‌سیم",
    summary:
      "مراحل تشخیص مشکل محلی دستگاه از اختلال عمومی Access Point.",
    category: "network",
    categoryLabelFa: categoryLabels.network,
    tags: ["Wi-Fi", "شبکه", "Access Point"],
    content:
      "## تشخیص سریع\n\nابتدا اتصال دستگاه دیگری را در همان محل بررسی کنید. اگر فقط یک دستگاه مشکل دارد، شبکه را Forget و دوباره متصل کنید.\n\nاگر چند دستگاه قطع هستند، نام طبقه و نزدیک‌ترین اتاق را در تیکت ثبت کنید.",
    updatedAt: "۱۴۰۵/۰۳/۰۳",
    author: "تیم شبکه",
  },
];

const vpnAnalysis: TicketAnalysis = {
  category: "vpn",
  categoryLabelFa: "مشکل VPN سازمان",
  intentLabelFa: "خطای احراز هویت لایه دسترسی دورکاری",
  urgency: "critical",
  confidence: 0.89,
  summaryFa:
    "کاربر به دلیل خطای احراز هویت نمی‌تواند به شبکه داخلی وصل شود. گزارش‌های هم‌زمان، احتمال اختلال عمومی در واحد فروش را بالا برده‌اند.",
  suggestedReplyFa:
    "سلام، درخواست شما دریافت شد. اختلال احراز هویت VPN در حال بررسی است. لطفاً اتصال را قطع کنید و ۱۰ دقیقه دیگر با نام کاربری سازمانی دوباره تلاش کنید. اگر مشکل ادامه داشت، همین تیکت را ارجاع دهید تا کارشناس به‌صورت مستقیم پیگیری کند.",
  reasonsFa: [
    "وجود عبارت‌های نشان‌دهنده توقف کامل کار و فوریت زمانی",
    "ثبت چند گزارش هم‌زمان با موضوع احراز هویت VPN",
    "انطباق معنایی بالا با رخدادهای قبلی سرویس دسترسی از راه دور",
  ],
  similarTickets: [
    { id: 106, title: "قطع اتصال VPN واحد مالی", score: 0.92 },
    { id: 102, title: "ورود ناموفق به سرویس‌های سازمانی", score: 0.81 },
  ],
  relatedArticle: {
    id: 12,
    title: seedArticles[0].title,
    score: 0.91,
  },
  possibleIncident: true,
};

const emailAnalysis: TicketAnalysis = {
  category: "email",
  categoryLabelFa: categoryLabels.email,
  intentLabelFa: "عدم همگام‌سازی بعد از تغییر رمز",
  urgency: "high",
  confidence: 0.94,
  summaryFa:
    "اطلاعات ورود قبلی Outlook پس از تغییر رمز عبور در سیستم باقی مانده و مانع همگام‌سازی صندوق ایمیل شده است.",
  suggestedReplyFa:
    "سلام، لطفاً Outlook را کامل ببندید، اطلاعات Office را از Credential Manager حذف کنید و برنامه را با رمز جدید باز کنید. در صورت حل نشدن، درخواست را ارجاع دهید تا کارشناس همراه شما بررسی کند.",
  reasonsFa: [
    "اشاره مستقیم به تغییر اخیر رمز عبور",
    "محدود بودن مشکل به ورود Outlook",
    "انطباق بالا با الگوی باقی‌ماندن Credential قدیمی",
  ],
  similarTickets: [
    { id: 107, title: "Outlook رمز جدید را قبول نمی‌کند", score: 0.9 },
  ],
  relatedArticle: {
    id: 13,
    title: seedArticles[1].title,
    score: 0.94,
  },
  possibleIncident: false,
};

const printerAnalysis: TicketAnalysis = {
  category: "printer",
  categoryLabelFa: categoryLabels.printer,
  intentLabelFa: "آفلاین بودن پرینتر شبکه",
  urgency: "medium",
  confidence: 0.84,
  summaryFa:
    "پرینتر طبقه دوم از شبکه خارج شده و صف چاپ چند کاربر را متوقف کرده است.",
  suggestedReplyFa:
    "سلام، ابتدا روشن بودن چراغ شبکه پرینتر و نبود خطای کاغذ را بررسی کنید. سپس صف چاپ را پاک کنید. اگر دستگاه همچنان Offline است، تیکت را ارجاع دهید.",
  reasonsFa: [
    "گزارش وضعیت Offline در چند سیستم",
    "محدود بودن اختلال به یک تجهیز مشخص",
    "نبود نشانه‌ای از توقف سرویس‌های حیاتی سازمان",
  ],
  similarTickets: [
    { id: 108, title: "پرینتر طبقه اول در دسترس نیست", score: 0.76 },
  ],
  relatedArticle: {
    id: 14,
    title: seedArticles[2].title,
    score: 0.88,
  },
  possibleIncident: false,
};

const accountAnalysis: TicketAnalysis = {
  category: "account",
  categoryLabelFa: categoryLabels.account,
  intentLabelFa: "درخواست سطح دسترسی توسعه‌دهنده",
  urgency: "low",
  confidence: 0.91,
  summaryFa:
    "کاربر برای انجام وظایف پروژه به سطح Developer در مخزن GitLab نیاز دارد.",
  suggestedReplyFa:
    "سلام، درخواست دسترسی ثبت شد. لطفاً نام دقیق مخزن و تأیید مدیر مستقیم را در همین تیکت ارسال کنید تا سطح Developer برای شما فعال شود.",
  reasonsFa: [
    "درخواست از نوع دسترسی و بدون نشانه اختلال است",
    "سطح دسترسی مورد نیاز به‌طور مشخص Developer ذکر شده",
    "فوریت عملیاتی یا توقف سرویس گزارش نشده است",
  ],
  similarTickets: [
    { id: 109, title: "دسترسی پروژه جدید GitLab", score: 0.89 },
  ],
  relatedArticle: {
    id: 15,
    title: seedArticles[3].title,
    score: 0.86,
  },
  possibleIncident: false,
};

export const seedTickets: Ticket[] = [
  {
    id: 101,
    title: "مشکل عدم اتصال به VPN سازمان",
    description:
      "خطای احراز هویت می‌دهد و نیم ساعت دیگر جلسه دارم. چند نفر از همکاران واحد فروش هم همین مشکل را دارند.",
    department: "واحد فروش",
    requesterId: "user-1",
    requesterName: "حسین احمدی",
    category: "vpn",
    categoryLabelFa: categoryLabels.vpn,
    urgency: "critical",
    status: "open",
    analysisStatus: "complete",
    confidence: 0.89,
    createdAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۰۰",
    updatedAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۰۲",
    analysis: vpnAnalysis,
  },
  {
    id: 102,
    title: "عدم باز شدن ایمیل بعد از تغییر رمز",
    description:
      "بعد از تغییر رمز عبور در اکتیو دایرکتوری دیگر نمی‌توانم وارد صندوق Outlook شوم.",
    department: "واحد مالی",
    requesterId: "user-2",
    requesterName: "سارا محمدی",
    category: "email",
    categoryLabelFa: categoryLabels.email,
    urgency: "high",
    status: "escalated",
    analysisStatus: "complete",
    confidence: 0.94,
    createdAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۰۵",
    updatedAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۲۰",
    analysis: emailAnalysis,
  },
  {
    id: 103,
    title: "آفلاین بودن پرینتر طبقه دوم",
    description:
      "پرینتر طبقه دوم آفلاین است و هیچ فایلی از سیستم‌های خط چاپ ارسال نمی‌شود.",
    department: "کارگاه تولید",
    requesterId: "user-3",
    requesterName: "مهدی کریمی",
    category: "printer",
    categoryLabelFa: categoryLabels.printer,
    urgency: "medium",
    status: "open",
    analysisStatus: "pending",
    confidence: 0,
    createdAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۰",
    updatedAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۰",
    analysis: null,
  },
  {
    id: 104,
    title: "درخواست دسترسی به مخازن GitLab",
    description:
      "برای پروژه جدید رادار نیاز به دسترسی Developer روی مخزن فرانت دارم.",
    department: "توسعه محصول",
    requesterId: "user-1",
    requesterName: "حسین احمدی",
    category: "account",
    categoryLabelFa: categoryLabels.account,
    urgency: "low",
    status: "resolved",
    analysisStatus: "complete",
    confidence: 0.91,
    createdAt: "۱۴۰۵/۰۳/۱۰ - ۱۶:۴۵",
    updatedAt: "۱۴۰۵/۰۳/۱۰ - ۱۷:۲۰",
    analysis: accountAnalysis,
  },
  {
    id: 105,
    title: "Outlook هنوز رمز جدید را قبول نمی‌کند",
    description:
      "مراحل حذف اطلاعات ذخیره‌شده را انجام دادم اما همچنان خطای ورود می‌گیرم و پاسخ خودکار مشکل را حل نکرد.",
    department: "واحد فروش",
    requesterId: "user-1",
    requesterName: "حسین احمدی",
    category: "email",
    categoryLabelFa: categoryLabels.email,
    urgency: "high",
    status: "escalated",
    analysisStatus: "complete",
    confidence: 0.9,
    createdAt: "۱۴۰۵/۰۳/۱۰ - ۱۴:۲۰",
    updatedAt: "۱۴۰۵/۰۳/۱۰ - ۱۴:۴۲",
    analysis: emailAnalysis,
  },
  {
    id: 106,
    title: "قطع اتصال VPN واحد مالی",
    description:
      "از ابتدای صبح اتصال VPN برای سه نفر از واحد مالی قطع و وصل می‌شود.",
    department: "واحد مالی",
    requesterId: "user-4",
    requesterName: "علی رضایی",
    category: "vpn",
    categoryLabelFa: categoryLabels.vpn,
    urgency: "high",
    status: "in_progress",
    analysisStatus: "complete",
    confidence: 0.87,
    createdAt: "۱۴۰۵/۰۳/۱۱ - ۰۹:۴۵",
    updatedAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۰",
    analysis: vpnAnalysis,
  },
];

export const seedIncidents: Incident[] = [
  {
    id: 201,
    title: "رخداد احتمالی در سرویس VPN",
    description:
      "افزایش گزارش‌های خطای احراز هویت و قطع اتصال در دو واحد سازمانی مشاهده شده است.",
    category: "vpn",
    categoryLabelFa: categoryLabels.vpn,
    severity: "critical",
    status: "candidate",
    detectedReason:
      "سه تیکت با شباهت معنایی بالاتر از ۸۵٪ در کمتر از ۳۰ دقیقه ثبت شده‌اند.",
    createdAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۲",
    tickets: [
      {
        ticketId: 101,
        title: "مشکل عدم اتصال به VPN سازمان",
        similarity: 0.94,
      },
      {
        ticketId: 106,
        title: "قطع اتصال VPN واحد مالی",
        similarity: 0.9,
      },
      {
        ticketId: 110,
        title: "خطای Authentication در Cisco",
        similarity: 0.86,
      },
    ],
  },
  {
    id: 202,
    title: "کندی موقت سرویس ایمیل",
    description:
      "چند گزارش پراکنده درباره تأخیر در دریافت ایمیل‌های بیرونی ثبت شده بود.",
    category: "email",
    categoryLabelFa: categoryLabels.email,
    severity: "medium",
    status: "resolved",
    detectedReason:
      "پنج گزارش در بازه دو ساعته با اشاره به تأخیر دریافت پیام ثبت شد.",
    createdAt: "۱۴۰۵/۰۳/۰۹ - ۱۲:۳۰",
    resolvedAt: "۱۴۰۵/۰۳/۰۹ - ۱۴:۱۰",
    tickets: [
      {
        ticketId: 111,
        title: "دریافت دیرهنگام ایمیل بیرونی",
        similarity: 0.82,
      },
      {
        ticketId: 112,
        title: "تأخیر در همگام‌سازی Inbox",
        similarity: 0.79,
      },
    ],
  },
];

export const seedAlerts: Alert[] = [
  {
    id: "alert-1",
    title: "رخداد احتمالی VPN",
    message: "خوشه جدیدی از خطاهای احراز هویت VPN شناسایی شد.",
    severity: "critical",
    type: "incident",
    createdAt: "۵ دقیقه پیش",
    read: false,
    href: "/incidents/201",
  },
  {
    id: "alert-3",
    title: "ارجاع جدید کاربر",
    message: "پاسخ AI مشکل کاربر واحد مالی را حل نکرده است.",
    severity: "high",
    type: "escalation",
    createdAt: "۲۱ دقیقه پیش",
    read: false,
    href: "/admin/escalated/esc-102",
  },
  {
    id: "alert-4",
    title: "تیکت فوری جدید",
    message: "تیکت جدیدی با نارضایتی بالا از واحد فروش دریافت شد.",
    severity: "high",
    type: "ticket",
    createdAt: "۳۲ دقیقه پیش",
    read: true,
    assignedAdminId: "admin-1",
    assignedAdminName: "مدیر پشتیبانی",
    href: "/tickets/101",
  },
];

export const seedSnapshot: AppSnapshot = {
  tickets: seedTickets,
  incidents: seedIncidents,
  articles: seedArticles,
  alerts: seedAlerts,
  escalations: [
    {
      id: "esc-102",
      ticketId: 102,
      requesterId: "user-2",
      requesterName: "سارا محمدی",
      reason:
        "Credential را حذف کردم اما Outlook هنوز خطای ورود نشان می‌دهد.",
      status: "waiting",
      createdAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۸",
      updatedAt: "۱۴۰۵/۰۳/۱۱ - ۱۰:۱۸",
      messages: [
        {
          id: "msg-102-1",
          senderId: "user-2",
          senderName: "سارا محمدی",
          senderRole: "user",
          text: "سلام، راه‌حل پیشنهادی را کامل انجام دادم ولی هنوز وارد ایمیل نمی‌شوم.",
          createdAt: "۱۰:۱۸",
        },
      ],
    },
    {
      id: "esc-105",
      ticketId: 105,
      requesterId: "user-1",
      requesterName: "حسین احمدی",
      reason: "پاسخ AI مشکل ورود با رمز جدید را حل نکرد.",
      status: "active",
      assignedAdminId: "admin-1",
      assignedAdminName: "مدیر پشتیبانی",
      createdAt: "۱۴۰۵/۰۳/۱۰ - ۱۴:۳۵",
      updatedAt: "۱۴۰۵/۰۳/۱۰ - ۱۴:۴۲",
      messages: [
        {
          id: "msg-105-1",
          senderId: "user-1",
          senderName: "حسین احمدی",
          senderRole: "user",
          text: "Credential Manager را پاک کردم ولی Outlook باز هم رمز را قبول نمی‌کند.",
          createdAt: "۱۴:۳۵",
        },
        {
          id: "msg-105-2",
          senderId: "admin-1",
          senderName: "مدیر پشتیبانی",
          senderRole: "admin",
          text: "سلام، حساب شما را بررسی می‌کنم. لطفاً بفرمایید ورود به وب‌میل هم خطا دارد؟",
          createdAt: "۱۴:۴۲",
        },
      ],
    },
  ],
};

export function buildMockAnalysis(
  title: string,
  description: string,
): TicketAnalysis {
  const text = `${title} ${description}`.toLowerCase();

  if (
    text.includes("vpn") ||
    text.includes("سیسکو") ||
    text.includes("دورکار")
  ) {
    return vpnAnalysis;
  }
  if (
    text.includes("ایمیل") ||
    text.includes("outlook") ||
    text.includes("صندوق")
  ) {
    return emailAnalysis;
  }
  if (text.includes("پرینتر") || text.includes("چاپ")) {
    return printerAnalysis;
  }
  return accountAnalysis;
}

export function cloneSeedSnapshot(): AppSnapshot {
  return JSON.parse(JSON.stringify(seedSnapshot)) as AppSnapshot;
}
