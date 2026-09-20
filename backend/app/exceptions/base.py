class AppError(Exception):
    #پایه همه خطاها
    #TODO: جهت ساخت یک اکسپشن هندلر سراری در FastAPI
    pass


class DuplicateEntityError(AppError):
    """موجودیت تکراری — پایه برای همه‌ی خطاهای duplicate."""
    pass


class PersistenceError(AppError):
    """خطای فنی در ذخیره‌سازی — پایه برای همه‌ی خطاهای DB."""
    pass