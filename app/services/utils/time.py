from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and a_end > b_start