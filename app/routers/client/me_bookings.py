from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.user_auth import get_current_user
from app.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.bookings import BookingResponse, MeBookingFilter
from app.services.utils.time import utc_now
from app.usecases.booking import cancel_booking_usecase

router = APIRouter(prefix="/me/bookings", tags=["Client Me"])

@router.get("", response_model=list[BookingResponse])
async def get_my_bookings(
    f: MeBookingFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Booking).where(Booking.user_id == current_user.id)
    now = utc_now()

    if f.type == "future":
        q = q.where(Booking.start_datetime >= now).order_by(Booking.start_datetime.asc())
    elif f.type == "past":
        q = q.where(Booking.start_datetime < now).order_by(Booking.start_datetime.desc())
    else:
        q = q.order_by(Booking.start_datetime.desc())

    return list((await db.scalars(q)).all())

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_my_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await cancel_booking_usecase(
        db=db, 
        booking_id=booking_id, 
        user_id=current_user.id
    )
    
    
