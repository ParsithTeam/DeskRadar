from app.exceptions.base import DuplicateEntityError, PersistenceError, AppError


class DuplicateTicketError(DuplicateEntityError):
    """
    این خطا زمانی raise می‌شود که تلاش برای ساخت تیکتی با
    fingerprint یکسان با تیکت موجود انجام شود.
    """
    pass


class TicketPersistenceError(PersistenceError):
    """
    این خطا زمانی raise می‌شود که DB خطای غیرمنتظره‌ای بدهد
    (اتصال قطع، timeout، constraint violation غیر از duplicate).
    """
    pass


class TicketNotFoundError(AppError):
    """تیکت مورد نظر پیدا نشد."""
    pass

