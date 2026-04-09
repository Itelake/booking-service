from datetime import date, datetime, time, timezone, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, MasterWorkingHours
from app.services.loyalty_service import calculate_discount_percent
from app.services.utils.time import utc_now
from app.schemas.bookings import BookingStatus
from app.services.utils.db_helpers import (
    get_master_or_404,
    get_service_or_404,
    get_master_service_or_404,
    get_booking_or_404,
    get_user_booking_or_404
)
from app.tasks import celery_app

ALMATY_TZ = ZoneInfo("Asia/Almaty")
ACTIVE_STATUSES = (BookingStatus.created.value, BookingStatus.confirmed.value)
VALID_ADMIN_TRANSITIONS = {
    BookingStatus.created.value: {BookingStatus.confirmed.value, BookingStatus.cancelled.value},
    BookingStatus.confirmed.value: {BookingStatus.done.value, BookingStatus.cancelled.value},
    BookingStatus.done.value: set(),
    BookingStatus.cancelled.value: set(),
}


def ensure_transition(old_status: str, new_status: str) -> None:
    allowed = VALID_ADMIN_TRANSITIONS.get(old_status, set())

    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid status transition: {old_status} -> {new_status}",
        )


async def create_booking_core(
    db: AsyncSession,
    user_id: int,
    master_id: int,
    service_id: int,
    date: date,
    start_time: time
):
    start_dt = datetime.combine(date, start_time, tzinfo=ALMATY_TZ)
    start_dt_utc = start_dt.astimezone(timezone.utc)

    await get_master_or_404(db, master_id, for_update=True)
    await get_service_or_404(db, service_id)

    ms = await get_master_service_or_404(db, master_id, service_id)

    if start_dt_utc <= utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create booking in the past",
        )

    start_local = start_dt
    weekday = start_local.date().weekday()

    wh = await db.scalar(
        select(MasterWorkingHours).where(
            MasterWorkingHours.master_id == master_id,
            MasterWorkingHours.weekday == weekday,
        )
    )
    if not wh:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Master does not work on this day",
        )

    work_start_local = datetime.combine(start_local.date(), wh.start_time, tzinfo=ALMATY_TZ)
    work_end_local = datetime.combine(start_local.date(), wh.end_time, tzinfo=ALMATY_TZ)

    end_local = start_local + timedelta(minutes=ms.duration_minutes)

    if not (work_start_local <= start_local and end_local <= work_end_local):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking time is outside master's working hours",
        )

    diff_minutes = int((start_local - work_start_local).total_seconds() // 60)
    if diff_minutes % ms.duration_minutes != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_datetime must align with service duration slots",
        )

    end_dt_utc = start_dt_utc + timedelta(minutes=ms.duration_minutes)

    conflict = await db.scalar(
        select(Booking.id).where(
            Booking.master_id == master_id,
            Booking.status.in_(ACTIVE_STATUSES),
            Booking.start_datetime < end_dt_utc,
            Booking.end_datetime > start_dt_utc   
        )
        .with_for_update()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is already booked",
        )
        
    price_at_booking = ms.price
    discount_percent = await calculate_discount_percent(db, user_id)
    
    final_price = price_at_booking - (price_at_booking * discount_percent // 100)   

    booking = Booking(
        user_id=user_id,
        master_id=master_id,
        service_id=service_id,
        start_datetime=start_dt_utc,
        end_datetime=end_dt_utc,
        status=BookingStatus.created.value,
        price_at_booking=price_at_booking,
        discount_percent_applied=discount_percent,
        final_price=final_price
    )
    
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
        
    return booking


async def cancel_booking_user(
    db: AsyncSession,
    booking_id: int,
    user_id: int
) -> Booking:
    booking = await get_user_booking_or_404(db, booking_id, user_id)
    
    if booking.status not in ACTIVE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking cannot be cancelled in this status"
        )
        
    if booking.start_datetime <= utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel after booking started"
        )
    
    booking.status = BookingStatus.cancelled.value
    
    if booking.reminder_24h_task_id:
        celery_app.control.revoke(booking.reminder_24h_task_id)

    if booking.reminder_2h_task_id:
        celery_app.control.revoke(booking.reminder_2h_task_id)
        
    booking.reminder_24h_task_id = None
    booking.reminder_2h_task_id = None
    
    await db.flush()
    await db.refresh(booking)
    return booking


async def admin_confirm_booking(db: AsyncSession, booking_id: int) -> Booking:
    booking = await get_booking_or_404(db, booking_id)
    
    ensure_transition(booking.status, BookingStatus.confirmed.value)

    if booking.start_datetime <= utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot confirm booking in the past",
        )

    booking.status = BookingStatus.confirmed.value

    await db.flush()
    await db.refresh(booking)

    return booking


async def admin_cancel_booking(db: AsyncSession, booking_id: int) -> Booking:
    booking = await get_booking_or_404(db, booking_id)

    ensure_transition(booking.status, BookingStatus.cancelled.value)
    booking.status = BookingStatus.cancelled.value

    await db.flush()
    await db.refresh(booking)

    return booking


async def admin_mark_done(db: AsyncSession, booking_id: int) -> Booking:
    booking = await get_booking_or_404(db, booking_id)

    ensure_transition(booking.status, BookingStatus.done.value)

    if booking.end_datetime > utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark as done before booking ends",
        )

    booking.status = BookingStatus.done.value

    await db.flush()
    await db.refresh(booking)

    return booking
