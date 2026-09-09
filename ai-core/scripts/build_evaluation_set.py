import json
from pathlib import Path

CASES = {
    "vpn": [
        ("وی پی ان وصل نمی‌شود و خطای احراز هویت می‌دهد", "vpn_authentication_error", "medium"),
        ("برای همکار جدید درخواست دسترسی VPN دارم", "vpn_request", "low"),
        ("اتصال vpn مدام قطع می‌شود و کارم عقب افتاده", "vpn_connection_issue", "high"),
        ("AnyConnect بعد از update اجرا نمی‌شود", "vpn_client_issue", "medium"),
        ("کد MFA برای ورود به وی پی ان تأیید نمی‌شود", "vpn_authentication_error", "medium"),
        ("لطفاً اکانت remote access من را فعال کنید", "vpn_request", "low"),
        ("نیم ساعت دیگر جلسه دارم و vpn connection failed است", "vpn_connection_issue", "high"),
        ("نسخه FortiClient قدیمی است و باید بروزرسانی شود", "vpn_client_issue", "low"),
    ],
    "email": [
        ("صندوق ایمیل پر شده و پیام جدید دریافت نمی‌کنم", "email_quota_issue", "medium"),
        ("رمز ایمیل را فراموش کرده‌ام و وارد نمی‌شوم", "email_access_issue", "medium"),
        ("ایمیل ارسال می‌شود ولی به گیرنده نمی‌رسد", "email_send_receive_issue", "medium"),
        ("Outlook sync نمی‌شود و پروفایل خطا دارد", "email_outlook_issue", "medium"),
        ("برای افزایش ظرفیت mailbox درخواست دارم", "email_quota_issue", "low"),
        ("حساب ایمیل قفل شده و جلسه فوری دارم", "email_access_issue", "high"),
        ("از صبح هیچ ایمیلی دریافت نکرده‌ام", "email_send_receive_issue", "medium"),
        ("فایل OST در Outlook باز نمی‌شود", "email_outlook_issue", "medium"),
    ],
    "network": [
        ("کل شرکت اینترنت ندارد و همه کاربران درگیرند", "network_drop", "critical"),
        ("سرعت اینترنت طبقه دوم خیلی کند شده", "network_speed", "medium"),
        ("وای فای لپ تاپ من شبکه را پیدا نمی‌کند", "network_wifi_issue", "medium"),
        ("کابل LAN وصل است ولی IP دریافت نمی‌شود", "network_lan_issue", "medium"),
        ("اینترنت سیستم من قطع شده و دسترسی ندارم", "network_drop", "high"),
        ("ping زیاد و latency شبکه بالا است", "network_speed", "medium"),
        ("SSID شرکت نمایش داده نمی‌شود", "network_wifi_issue", "medium"),
        ("پورت شبکه اتاق مالی کار نمی‌کند", "network_lan_issue", "medium"),
    ],
    "printer": [
        ("پرینتر خطای paper jam می‌دهد", "printer_error", "medium"),
        ("فایل‌ها در صف چاپ گیر کرده‌اند", "print_queue", "medium"),
        ("تونر پرینتر تمام شده و چاپ کم‌رنگ است", "printer_supply_issue", "low"),
        ("درخواست نصب پرینتر جدید روی سیستم دارم", "printer_setup_request", "low"),
        ("پرینتر واحد مالی offline شده", "printer_error", "medium"),
        ("job چاپ pending مانده و حذف نمی‌شود", "print_queue", "medium"),
        ("کارتریج دستگاه نیاز به تعویض دارد", "printer_supply_issue", "low"),
        ("لطفاً driver چاپگر را نصب کنید", "printer_setup_request", "low"),
    ],
    "account": [
        ("رمز حساب را فراموش کردم و اکانت قفل شده", "account_lock", "medium"),
        ("برای نیروی جدید حساب کاربری بسازید", "account_creation", "low"),
        ("به پورتال سازمانی login نمی‌شوم", "account_access_issue", "medium"),
        ("لطفاً حساب کاربر قبلی را غیرفعال کنید", "account_deactivation", "low"),
        ("password منقضی شده و امکان ورود ندارم", "account_lock", "medium"),
        ("درخواست create account برای همکار فروش دارم", "account_creation", "low"),
        ("خطای access denied هنگام ورود به سامانه دارم", "account_access_issue", "medium"),
        ("اکانت همکار جداشده باید disable شود", "account_deactivation", "low"),
    ],
    "hardware": [
        ("لپ تاپ روشن نمی‌شود و چراغ پاور خاموش است", "hardware_failure", "medium"),
        ("برای همکار جدید مانیتور درخواست دارم", "hardware_request", "low"),
        ("موس و کیبورد روی هیچ پورتی کار نمی‌کنند", "hardware_peripheral_issue", "medium"),
        ("مانیتور تصویر ندارد ولی سیستم روشن است", "hardware_display_issue", "medium"),
        ("هارد دستگاه خراب شده و سیستم بالا نمی‌آید", "hardware_failure", "high"),
        ("یک هدست برای تماس‌های واحد فروش لازم دارم", "hardware_request", "low"),
        ("کیبورد چند کلید را ثبت نمی‌کند", "hardware_peripheral_issue", "low"),
        ("تصویر مانیتور پرش دارد و کابل سالم است", "hardware_display_issue", "medium"),
    ],
    "software": [
        ("لطفاً نرم افزار حسابداری را نصب کنید", "software_install", "low"),
        ("برنامه هنگام اجرا crash می‌کند و error می‌دهد", "software_error", "medium"),
        ("لایسنس نرم افزار منقضی شده است", "software_license_issue", "medium"),
        ("برای دسترسی به برنامه CRM درخواست دارم", "software_access_request", "low"),
        ("نسخه جدید نرم‌افزار باید update شود", "software_install", "low"),
        ("اپلیکیشن باز نمی‌شود و کارم متوقف شده", "software_error", "high"),
        ("activation برنامه ناموفق است", "software_license_issue", "medium"),
        ("مجوز استفاده از نرم افزار گزارش‌گیری لازم دارم", "software_access_request", "low"),
    ],
    "permission": [
        ("برای پوشه اشتراکی خطای access denied دارم", "permission_denied", "medium"),
        ("درخواست دسترسی خواندن به فایل مالی دارم", "permission_request", "low"),
        ("مسیر shared folder باز نمی‌شود", "shared_folder_issue", "medium"),
        ("دسترسی کاربر قبلی به پوشه باید حذف شود", "permission_remove_access", "low"),
        ("مجوز ورود به فولدر پروژه را ندارم", "permission_denied", "medium"),
        ("لطفاً permission نوشتن روی فایل را اضافه کنید", "permission_request", "low"),
        ("فایل روی شبکه پیدا نمی‌شود و پوشه قطع است", "shared_folder_issue", "medium"),
        ("درخواست remove access کاربر مهمان را دارم", "permission_remove_access", "low"),
    ],
}


def main() -> None:
    rows = []
    for category, cases in CASES.items():
        if len(cases) != 8:
            raise ValueError(f"{category} must contain exactly 8 cases")
        for index, (text, intent, urgency) in enumerate(cases, start=1):
            rows.append(
                {
                    "ticket_id": f"EVAL-{category.upper()}-{index:02d}",
                    "text": text,
                    "expected_category": category,
                    "expected_intent": intent,
                    "expected_urgency": urgency,
                }
            )

    output = Path(__file__).resolve().parents[1] / "data/evaluation/analyzer_eval_set.json"
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} evaluation cases to {output}")


if __name__ == "__main__":
    main()
