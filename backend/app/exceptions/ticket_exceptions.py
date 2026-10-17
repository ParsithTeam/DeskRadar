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



class TicketRequesterNotFoundError(AppError):
    """The user referenced by requester does not exist."""

    def __init__(self, requester: int):
        self.requester = requester
        super().__init__(f"User with id {requester} does not exist.")
