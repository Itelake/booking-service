# app/routers/admin/bookings.py
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.booking import Booking
from app.schemas.bookings import BookingFilter, Pagination, PaginatedBookingResponse, BookingResponse
from app.services.booking_service import admin_confirm_booking, admin_cancel_booking, admin_mark_done

router = APIRouter(prefix="/bookings", tags=["Admin Bookings"])

@router.get("", response_model=PaginatedBookingResponse)
async def get_all_bookings(
    f: BookingFilter = Depends(),
    p: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    conditions = []

    if f.status is not None:
        conditions.append(Booking.status == f.status.value)
    if f.master_id is not None:
        conditions.append(Booking.master_id == f.master_id)
    if f.service_id is not None:
        conditions.append(Booking.service_id == f.service_id)
    if f.user_id is not None:
        conditions.append(Booking.user_id == f.user_id)
    if f.date_from is not None:
        conditions.append(Booking.start_datetime >= f.date_from)
    if f.date_to is not None:
        conditions.append(Booking.start_datetime <= f.date_to)

    total = await db.scalar(select(func.count(Booking.id)).where(*conditions))
    total = int(total or 0)

    q_items = (
        select(Booking)
        .where(*conditions)
        .order_by(Booking.start_datetime.asc())
        .limit(p.limit)
        .offset(p.offset)
    )
    items = (await db.scalars(q_items)).all()

    return {"items": list(items), "total": total, "limit": p.limit, "offset": p.offset}


@router.patch("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_bookings(booking_id: int, db: AsyncSession = Depends(get_db)):
    return await admin_confirm_booking(db, booking_id)

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_bookings(booking_id: int, db: AsyncSession = Depends(get_db)):
    return await admin_cancel_booking(db, booking_id)

@router.patch("/{booking_id}/done", response_model=BookingResponse)
async def done_bookings(booking_id: int, db: AsyncSession = Depends(get_db)):
    return await admin_mark_done(db, booking_id)