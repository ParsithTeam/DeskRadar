"""Timezone-aware UTC timestamps shared by models and repositories."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def as_utc(value: datetime | None) -> datetime | None:
    """Normalize a value read from the DB to UTC for serialization.

    Legacy TIMESTAMP WITHOUT TIME ZONE values are assumed to contain UTC wall
    times. If historical rows were stored in local time, convert them in a
    separate, carefully reviewed data migration instead.
    """
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

