from .normalizer import normalize_persian_text
from .reply_tone import select_reply_tone

DEFAULT_REPLY = {
    "title": "پاسخ عمومی",
    "message": (
        "سلام، تیکت شما دریافت شد. لطفاً جزئیات بیشتر، تصویر خطا و زمان شروع مشکل را ارسال کنید "
        "تا بررسی دقیق‌تر انجام شود."
    ),
    "required_info": [
        "زمان شروع مشکل",
        "تصویر یا متن خطا",
        "نام سامانه یا سرویس مربوطه",
    ],
}


CATEGORY_REPLY_TEMPLATES = {
    "vpn": {
        "title": "بررسی مشکل VPN",
        "message": (
            "سلام، لطفاً اتصال اینترنت خود را بررسی کرده و سپس VPN را یک‌بار قطع و دوباره وصل کنید. "
            "در صورت ادامه مشکل، تصویر خطا و نام نرم‌افزار VPN مورد استفاده را ارسال کنید."
        ),
        "required_info": [
            "تصویر خطای VPN",
            "نام نرم‌افزار VPN",
            "نوع اینترنت مورد استفاده",
        ],
    },
    "email": {
        "title": "بررسی مشکل ایمیل",
        "message": (
            "سلام، لطفاً سرویس ایمیل یا Outlook را یک‌بار بسته و دوباره باز کنید. "
            "در صورت ادامه مشکل، تصویر خطا و آدرس ایمیل سازمانی خود را ارسال کنید."
        ),
        "required_info": [
            "آدرس ایمیل سازمانی",
            "تصویر خطا",
            "زمان شروع مشکل",
        ],
    },
    "network": {
        "title": "بررسی مشکل شبکه یا اینترنت",
        "message": (
            "سلام، لطفاً اتصال کابل شبکه یا Wi-Fi را بررسی کنید. "
            "در صورت ادامه مشکل، محل حضور، نوع اتصال و زمان شروع مشکل را ارسال کنید."
        ),
        "required_info": [
            "محل یا طبقه",
            "نوع اتصال: کابل یا Wi-Fi",
            "زمان شروع مشکل",
        ],
    },
    "printer": {
        "title": "بررسی مشکل پرینتر",
        "message": (
            "سلام، لطفاً روشن بودن پرینتر، وجود کاغذ و وضعیت صف چاپ را بررسی کنید. "
            "اگر خطا نمایش داده می‌شود، تصویر خطا و نام یا مدل پرینتر را ارسال کنید."
        ),
        "required_info": [
            "نام یا مدل پرینتر",
            "تصویر خطا",
            "محل قرارگیری پرینتر",
        ],
    },
    "account": {
        "title": "بررسی حساب کاربری",
        "message": (
            "سلام، تیکت شما برای بررسی حساب کاربری دریافت شد. "
            "لطفاً نام کاربری، نام سامانه و در صورت وجود تصویر خطا را ارسال کنید."
        ),
        "required_info": [
            "نام کاربری",
            "نام سامانه",
            "تصویر خطا",
        ],
    },
    "hardware": {
        "title": "بررسی مشکل سخت‌افزار",
        "message": (
            "سلام، لطفاً دستگاه را یک‌بار خاموش و روشن کنید و کابل‌های برق یا اتصال را بررسی کنید. "
            "در صورت ادامه مشکل، نوع دستگاه، شماره اموال و محل استقرار را ارسال کنید."
        ),
        "required_info": [
            "نوع دستگاه",
            "شماره اموال",
            "محل استقرار",
        ],
    },
    "software": {
        "title": "بررسی مشکل نرم‌افزار",
        "message": (
            "سلام، لطفاً نرم‌افزار را یک‌بار بسته و دوباره اجرا کنید. "
            "در صورت ادامه مشکل، نام نرم‌افزار، نسخه آن و تصویر خطا را ارسال کنید."
        ),
        "required_info": [
            "نام نرم‌افزار",
            "نسخه نرم‌افزار",
            "تصویر خطا",
        ],
    },
    "permission": {
        "title": "بررسی دسترسی فایل یا پوشه",
        "message": (
            "سلام، لطفاً مسیر فایل یا پوشه، نوع دسترسی موردنیاز و نام کاربری خود را ارسال کنید "
            "تا سطح دسترسی بررسی شود."
        ),
        "required_info": [
            "مسیر فایل یا پوشه",
            "نوع دسترسی موردنیاز",
            "نام کاربری",
        ],
    },
}


INTENT_REPLY_TEMPLATES = {
    "vpn_request": {
        "title": "درخواست دسترسی VPN",
        "message": (
            "سلام، برای ایجاد یا فعال‌سازی دسترسی VPN، لطفاً نام کاربری، واحد سازمانی "
            "و دلیل نیاز به دسترسی را ارسال کنید."
        ),
        "required_info": [
            "نام کاربری",
            "واحد سازمانی",
            "دلیل نیاز به VPN",
        ],
    },
    "vpn_authentication_error": {
        "title": "خطای احراز هویت VPN",
        "message": (
            "سلام، لطفاً رمز عبور و کد احراز هویت را دوباره بررسی کنید. "
            "در صورت ادامه خطا، تصویر خطا، نام کاربری و زمان رخ دادن مشکل را ارسال کنید."
        ),
        "required_info": [
            "تصویر خطای احراز هویت",
            "نام کاربری",
            "زمان رخ دادن مشکل",
        ],
    },
    "vpn_connection_issue": {
        "title": "مشکل اتصال VPN",
        "message": (
            "سلام، لطفاً اتصال اینترنت را بررسی کرده و VPN را یک‌بار قطع و دوباره وصل کنید. "
            "اگر اتصال برقرار نشد، تصویر خطا و نام نرم‌افزار VPN را ارسال کنید."
        ),
        "required_info": [
            "تصویر خطا",
            "نام نرم‌افزار VPN",
            "نوع اینترنت",
        ],
    },
    "vpn_client_issue": {
        "title": "مشکل کلاینت VPN",
        "message": (
            "سلام، لطفاً نسخه نرم‌افزار VPN و تصویر خطای نمایش‌داده‌شده را ارسال کنید. "
            "در صورت نیاز، نصب یا بروزرسانی کلاینت بررسی می‌شود."
        ),
        "required_info": [
            "نام کلاینت VPN",
            "نسخه نرم‌افزار",
            "تصویر خطا",
        ],
    },
    "email_quota_issue": {
        "title": "مشکل حجم ایمیل",
        "message": (
            "سلام، لطفاً آدرس ایمیل سازمانی و تصویر پیام خطای مربوط به حجم صندوق پستی را ارسال کنید. "
            "همچنین می‌توانید ایمیل‌های قدیمی یا فایل‌های حجیم را بررسی و پاکسازی کنید."
        ),
        "required_info": [
            "آدرس ایمیل سازمانی",
            "تصویر پیام خطا",
            "حجم تقریبی صندوق پستی",
        ],
    },
    "email_access_issue": {
        "title": "مشکل ورود به ایمیل",
        "message": (
            "سلام، لطفاً آدرس ایمیل سازمانی و تصویر خطای ورود را ارسال کنید. "
            "در صورت نیاز، وضعیت حساب و رمز عبور بررسی می‌شود."
        ),
        "required_info": [
            "آدرس ایمیل سازمانی",
            "تصویر خطای ورود",
            "زمان شروع مشکل",
        ],
    },
    "email_send_receive_issue": {
        "title": "مشکل ارسال یا دریافت ایمیل",
        "message": (
            "سلام، لطفاً مشخص کنید مشکل در ارسال ایمیل است یا دریافت آن. "
            "همچنین پیام خطا، آدرس گیرنده یا فرستنده و زمان رخ دادن مشکل را ارسال کنید."
        ),
        "required_info": [
            "نوع مشکل: ارسال یا دریافت",
            "پیام خطا",
            "آدرس گیرنده یا فرستنده",
        ],
    },
    "email_outlook_issue": {
        "title": "مشکل Outlook",
        "message": (
            "سلام، لطفاً Outlook را یک‌بار بسته و دوباره باز کنید. "
            "اگر مشکل همگام‌سازی یا اجرای Outlook ادامه داشت، تصویر خطا و نسخه Outlook را ارسال کنید."
        ),
        "required_info": [
            "تصویر خطا",
            "نسخه Outlook",
            "زمان شروع مشکل",
        ],
    },
    "network_drop": {
        "title": "قطعی شبکه یا اینترنت",
        "message": (
            "سلام، لطفاً مشخص کنید مشکل برای یک سیستم رخ داده یا چند کاربر هم درگیر هستند. "
            "همچنین محل، نوع اتصال و زمان شروع قطعی را ارسال کنید."
        ),
        "required_info": [
            "محل یا طبقه",
            "نوع اتصال",
            "تعداد کاربران درگیر",
        ],
    },
    "network_speed": {
        "title": "کندی شبکه یا اینترنت",
        "message": (
            "سلام، لطفاً نوع اتصال، محل حضور و زمان‌هایی که کندی بیشتر رخ می‌دهد را ارسال کنید. "
            "در صورت امکان نتیجه ping یا تصویر خطا را هم ضمیمه کنید."
        ),
        "required_info": [
            "محل",
            "نوع اتصال",
            "زمان رخ دادن کندی",
        ],
    },
    "network_wifi_issue": {
        "title": "مشکل Wi-Fi",
        "message": (
            "سلام، لطفاً نام شبکه Wi-Fi، محل حضور و اینکه سایر کاربران هم مشکل دارند یا خیر را ارسال کنید. "
            "در صورت امکان یک‌بار اتصال Wi-Fi را قطع و دوباره وصل کنید."
        ),
        "required_info": [
            "نام Wi-Fi",
            "محل حضور",
            "وضعیت سایر کاربران",
        ],
    },
    "network_lan_issue": {
        "title": "مشکل شبکه کابلی",
        "message": (
            "سلام، لطفاً کابل شبکه و پورت را بررسی کنید. "
            "اگر مشکل ادامه داشت، محل سیستم، شماره پورت یا اتاق و زمان شروع مشکل را ارسال کنید."
        ),
        "required_info": [
            "محل سیستم",
            "شماره اتاق یا پورت",
            "زمان شروع مشکل",
        ],
    },
    "printer_error": {
        "title": "خطای پرینتر",
        "message": (
            "سلام، لطفاً وضعیت کاغذ، روشن بودن دستگاه و خطای نمایش‌داده‌شده روی پرینتر را بررسی کنید. "
            "در صورت ادامه مشکل، تصویر خطا و مدل پرینتر را ارسال کنید."
        ),
        "required_info": [
            "مدل یا نام پرینتر",
            "تصویر خطا",
            "محل پرینتر",
        ],
    },
    "print_queue": {
        "title": "مشکل صف چاپ",
        "message": (
            "سلام، لطفاً وضعیت صف چاپ را بررسی کنید و در صورت امکان jobهای قدیمی را حذف کنید. "
            "اگر چاپ انجام نشد، نام پرینتر و نام فایل موردنظر را ارسال کنید."
        ),
        "required_info": [
            "نام پرینتر",
            "نام فایل",
            "تصویر وضعیت صف چاپ",
        ],
    },
    "printer_supply_issue": {
        "title": "مشکل تونر یا کارتریج",
        "message": (
            "سلام، لطفاً مدل پرینتر و وضعیت تونر یا کارتریج را ارسال کنید. "
            "در صورت وجود پیام خطا یا کیفیت پایین چاپ، تصویر نمونه چاپ را هم ضمیمه کنید."
        ),
        "required_info": [
            "مدل پرینتر",
            "وضعیت تونر یا کارتریج",
            "نمونه چاپ در صورت نیاز",
        ],
    },
    "printer_setup_request": {
        "title": "درخواست نصب پرینتر",
        "message": (
            "سلام، لطفاً نام یا مدل پرینتر، محل نصب و نام کاربری سیستم مقصد را ارسال کنید "
            "تا نصب یا تعریف پرینتر بررسی شود."
        ),
        "required_info": [
            "نام یا مدل پرینتر",
            "محل نصب",
            "نام کاربری سیستم مقصد",
        ],
    },
    "account_lock": {
        "title": "قفل یا فراموشی رمز حساب",
        "message": (
            "سلام، لطفاً نام کاربری و نام سامانه‌ای که امکان ورود به آن را ندارید ارسال کنید. "
            "در صورت وجود پیام خطا، تصویر آن را هم ضمیمه کنید."
        ),
        "required_info": [
            "نام کاربری",
            "نام سامانه",
            "تصویر خطا",
        ],
    },
    "account_creation": {
        "title": "درخواست ایجاد حساب کاربری",
        "message": (
            "سلام، برای ایجاد حساب کاربری جدید، لطفاً نام و نام خانوادگی کاربر، واحد سازمانی، "
            "سمت و سطح دسترسی موردنیاز را ارسال کنید."
        ),
        "required_info": [
            "نام و نام خانوادگی",
            "واحد سازمانی",
            "سطح دسترسی موردنیاز",
        ],
    },
    "account_access_issue": {
        "title": "مشکل دسترسی به حساب یا سامانه",
        "message": (
            "سلام، لطفاً نام کاربری، نام سامانه و تصویر خطای نمایش‌داده‌شده را ارسال کنید "
            "تا وضعیت دسترسی بررسی شود."
        ),
        "required_info": [
            "نام کاربری",
            "نام سامانه",
            "تصویر خطا",
        ],
    },
    "account_deactivation": {
        "title": "درخواست غیرفعال‌سازی حساب",
        "message": (
            "سلام، برای غیرفعال‌سازی یا حذف حساب، لطفاً نام کاربری، واحد سازمانی "
            "و دلیل درخواست را ارسال کنید."
        ),
        "required_info": [
            "نام کاربری",
            "واحد سازمانی",
            "دلیل درخواست",
        ],
    },
    "hardware_failure": {
        "title": "خرابی سخت‌افزار",
        "message": (
            "سلام، لطفاً نوع دستگاه، وضعیت چراغ‌ها یا خطای قابل مشاهده، شماره اموال "
            "و محل استقرار دستگاه را ارسال کنید."
        ),
        "required_info": [
            "نوع دستگاه",
            "شماره اموال",
            "محل استقرار",
        ],
    },
    "hardware_request": {
        "title": "درخواست تجهیزات سخت‌افزاری",
        "message": (
            "سلام، لطفاً نوع تجهیز موردنیاز، دلیل درخواست، واحد سازمانی "
            "و نام کاربر دریافت‌کننده را ارسال کنید."
        ),
        "required_info": [
            "نوع تجهیز",
            "دلیل درخواست",
            "نام کاربر دریافت‌کننده",
        ],
    },
    "hardware_peripheral_issue": {
        "title": "مشکل تجهیزات جانبی",
        "message": (
            "سلام، لطفاً نوع تجهیز جانبی، مدل یا نام دستگاه و توضیح مشکل را ارسال کنید. "
            "در صورت امکان، تجهیز را روی یک پورت یا سیستم دیگر هم تست کنید."
        ),
        "required_info": [
            "نوع تجهیز جانبی",
            "مدل یا نام دستگاه",
            "محل استقرار",
        ],
    },
    "hardware_display_issue": {
        "title": "مشکل تصویر یا نمایشگر",
        "message": (
            "سلام، لطفاً کابل تصویر و برق مانیتور را بررسی کنید. "
            "اگر مشکل ادامه داشت، مدل مانیتور، نوع اتصال و تصویر وضعیت نمایشگر را ارسال کنید."
        ),
        "required_info": [
            "مدل مانیتور",
            "نوع اتصال",
            "تصویر وضعیت نمایشگر",
        ],
    },
    "software_install": {
        "title": "درخواست نصب یا بروزرسانی نرم‌افزار",
        "message": (
            "سلام، لطفاً نام نرم‌افزار، نسخه موردنیاز و دلیل نصب یا بروزرسانی را ارسال کنید. "
            "در صورت نیاز، مجوز نصب بررسی می‌شود."
        ),
        "required_info": [
            "نام نرم‌افزار",
            "نسخه موردنیاز",
            "دلیل درخواست",
        ],
    },
    "software_error": {
        "title": "خطای نرم‌افزار",
        "message": (
            "سلام، لطفاً نام نرم‌افزار، نسخه آن، تصویر خطا و کاری که قبل از خطا انجام داده‌اید را ارسال کنید."
        ),
        "required_info": [
            "نام نرم‌افزار",
            "نسخه نرم‌افزار",
            "تصویر خطا",
        ],
    },
    "software_license_issue": {
        "title": "مشکل لایسنس نرم‌افزار",
        "message": (
            "سلام، لطفاً نام نرم‌افزار، پیام خطای لایسنس و نام کاربری یا سیستم موردنظر را ارسال کنید "
            "تا وضعیت مجوز بررسی شود."
        ),
        "required_info": [
            "نام نرم‌افزار",
            "پیام خطای لایسنس",
            "نام کاربری یا نام سیستم",
        ],
    },
    "software_access_request": {
        "title": "درخواست دسترسی نرم‌افزار",
        "message": (
            "سلام، لطفاً نام نرم‌افزار، نوع دسترسی موردنیاز، دلیل درخواست و نام کاربری را ارسال کنید."
        ),
        "required_info": [
            "نام نرم‌افزار",
            "نوع دسترسی موردنیاز",
            "نام کاربری",
        ],
    },
    "permission_denied": {
        "title": "خطای عدم دسترسی",
        "message": (
            "سلام، لطفاً مسیر فایل، پوشه یا سامانه‌ای که به آن دسترسی ندارید، تصویر خطا "
            "و نوع دسترسی موردنیاز را ارسال کنید."
        ),
        "required_info": [
            "مسیر فایل یا پوشه",
            "تصویر خطا",
            "نوع دسترسی موردنیاز",
        ],
    },
    "permission_request": {
        "title": "درخواست مجوز دسترسی",
        "message": (
            "سلام، لطفاً مسیر فایل یا پوشه، نوع دسترسی موردنیاز، نام کاربری "
            "و دلیل درخواست دسترسی را ارسال کنید."
        ),
        "required_info": [
            "مسیر فایل یا پوشه",
            "نوع دسترسی موردنیاز",
            "دلیل درخواست",
        ],
    },
    "shared_folder_issue": {
        "title": "مشکل فایل یا پوشه اشتراکی",
        "message": (
            "سلام، لطفاً مسیر پوشه یا فایل اشتراکی، تصویر خطا و نوع دسترسی موردنیاز را ارسال کنید."
        ),
        "required_info": [
            "مسیر فایل یا پوشه اشتراکی",
            "تصویر خطا",
            "نوع دسترسی موردنیاز",
        ],
    },
    "permission_remove_access": {
        "title": "درخواست حذف دسترسی",
        "message": (
            "سلام، لطفاً نام کاربری، مسیر فایل یا پوشه و نوع دسترسی‌ای که باید حذف شود را ارسال کنید."
        ),
        "required_info": [
            "نام کاربری",
            "مسیر فایل یا پوشه",
            "نوع دسترسی قابل حذف",
        ],
    },
}


URGENCY_PREFIX = {
    "critical": ("با توجه به بحرانی بودن موضوع، این تیکت باید با اولویت بسیار بالا بررسی شود. "),
    "high": ("با توجه به فوریت بالای موضوع، این تیکت باید در اولویت بررسی قرار گیرد. "),
    "medium": "",
    "low": "",
    "unknown": "",
}


SENTIMENT_PREFIX = {
    "angry": ("ضمن عذرخواهی بابت مشکل پیش‌آمده، "),
    "frustrated": ("ضمن عذرخواهی بابت تأخیر یا تکرار مشکل، "),
    "negative": "",
    "neutral": "",
    "positive": "",
    "unknown": "",
}


ESCALATION_HINTS = {
    "critical": "ارجاع فوری به تیم پشتیبانی سطح دو یا مسئول سرویس پیشنهاد می‌شود.",
    "high": "در صورت عدم رفع سریع، ارجاع به تیم تخصصی پیشنهاد می‌شود.",
    "medium": "بررسی طبق روال عادی پشتیبانی کافی است.",
    "low": "بررسی در زمان مناسب طبق صف تیکت‌ها کافی است.",
    "unknown": "پس از دریافت اطلاعات بیشتر، سطح ارجاع مشخص شود.",
}


def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def unique_items(items: list) -> list:
    result = []
    seen = set()

    for item in items:
        clean_item = str(item).strip()

        if clean_item and clean_item not in seen:
            result.append(clean_item)
            seen.add(clean_item)

    return result


def get_base_template(category: str, intent: str) -> dict:
    category_code = normalize_value(category)
    intent_code = normalize_value(intent)

    if intent_code in INTENT_REPLY_TEMPLATES:
        return INTENT_REPLY_TEMPLATES[intent_code]

    if category_code in CATEGORY_REPLY_TEMPLATES:
        return CATEGORY_REPLY_TEMPLATES[category_code]

    return DEFAULT_REPLY


def build_internal_notes(
    category: str,
    intent: str,
    urgency_level: str,
    sentiment: str,
    text: str,
) -> list:
    notes = []
    category_code = normalize_value(category)
    intent_code = normalize_value(intent)
    urgency_code = normalize_value(urgency_level)
    sentiment_code = normalize_value(sentiment)
    clean_text = normalize_persian_text(text)

    if category_code:
        notes.append(f"Category: {category_code}")

    if intent_code:
        notes.append(f"Intent: {intent_code}")

    if urgency_code:
        notes.append(f"Urgency: {urgency_code}")

    if sentiment_code:
        notes.append(f"Sentiment: {sentiment_code}")

    if "error" in clean_text:
        notes.append("از کاربر تصویر یا متن کامل خطا دریافت شود.")

    if urgency_code in ["critical", "high"]:
        notes.append("زمان پاسخ‌گویی باید کوتاه‌تر از حالت عادی باشد.")

    if sentiment_code in ["angry", "frustrated"]:
        notes.append("پاسخ با لحن آرام، همدلانه و شفاف ارسال شود.")

    return notes


def build_reply(
    text: str,
    category: str = "",
    intent: str = "",
    urgency_level: str = "",
    sentiment: str = "",
) -> dict:
    clean_text = normalize_persian_text(text)

    if not clean_text:
        return {
            "reply_title": "متن نامعتبر",
            "suggested_reply": (
                "سلام، متن تیکت دریافت نشده است. لطفاً مشکل خود را با جزئیات بیشتر ارسال کنید."
            ),
            "required_info": [
                "شرح مشکل",
                "زمان شروع مشکل",
                "تصویر خطا در صورت وجود",
            ],
            "escalation_hint": "پس از دریافت متن تیکت، سطح ارجاع مشخص شود.",
            "internal_notes": [
                "متن تیکت خالی است.",
            ],
            "reply_tone": "standard",
            "reply_tone_label_fa": "عادی",
        }

    category_code = normalize_value(category)
    intent_code = normalize_value(intent)
    urgency_code = normalize_value(urgency_level)
    sentiment_code = normalize_value(sentiment)

    template = get_base_template(category_code, intent_code)
    tone_result = select_reply_tone(
        sentiment=sentiment_code,
        urgency_level=urgency_code,
        category=category_code,
    )

    message = str(template["message"]).strip()
    if message.startswith("سلام،"):
        message = message.removeprefix("سلام،").lstrip()

    prefix = SENTIMENT_PREFIX.get(sentiment_code, "")
    prefix += URGENCY_PREFIX.get(urgency_code, "")
    suggested_reply = f"سلام، {prefix}{message}".strip()
    required_info = unique_items(template.get("required_info", []))
    internal_notes = build_internal_notes(
        category=category_code,
        intent=intent_code,
        urgency_level=urgency_code,
        sentiment=sentiment_code,
        text=text,
    )

    return {
        "reply_title": template["title"],
        "suggested_reply": suggested_reply,
        "required_info": required_info,
        "escalation_hint": ESCALATION_HINTS.get(
            urgency_code,
            ESCALATION_HINTS["unknown"],
        ),
        "internal_notes": internal_notes,
        **tone_result,
    }


def create_suggested_reply(
    text: str,
    category: str = "",
    intent: str = "",
    urgency_level: str = "",
    sentiment: str = "",
) -> str:
    return build_reply(
        text=text,
        category=category,
        intent=intent,
        urgency_level=urgency_level,
        sentiment=sentiment,
    )["suggested_reply"]


if __name__ == "__main__":
    samples = [
        {
            "text": "سلام، من نیم ساعت دیگه جلسه دارم ولی vpn قطعه و احراز هویت نمیکنه",
            "category": "vpn",
            "intent": "vpn_authentication_error",
            "urgency_level": "high",
            "sentiment": "negative",
        },
        {
            "text": "چند بار اعلام کردم هنوز ایمیل من درست نشده و کسی جواب نمیده",
            "category": "email",
            "intent": "email_access_issue",
            "urgency_level": "high",
            "sentiment": "frustrated",
        },
        {
            "text": "هر وقت فرصت داشتید لطفا پرینتر اتاق من را بررسی کنید",
            "category": "printer",
            "intent": "printer_error",
            "urgency_level": "low",
            "sentiment": "positive",
        },
        {
            "text": "کل شرکت اینترنت ندارد و همه کاربران درگیر هستند",
            "category": "network",
            "intent": "network_drop",
            "urgency_level": "critical",
            "sentiment": "angry",
        },
    ]

    for sample in samples:
        print(
            build_reply(
                text=sample["text"],
                category=sample["category"],
                intent=sample["intent"],
                urgency_level=sample["urgency_level"],
                sentiment=sample["sentiment"],
            )
        )
