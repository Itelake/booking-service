import pytest
from fastapi import HTTPException

from app.services.booking_service import ensure_transition # если нужно
from app.schemas.bookings import BookingStatus


def test_ensure_transition_ok_created_to_confirmed():
    ensure_transition(BookingStatus.created.value, BookingStatus.confirmed.value)


def test_ensure_transition_invalid_raises_409():
    with pytest.raises(HTTPException) as e:
        ensure_transition(BookingStatus.done.value, BookingStatus.confirmed.value)

    assert e.value.status_code == 409
    assert "Invalid status transition" in e.value.detail