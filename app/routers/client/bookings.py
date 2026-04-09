from datetime import timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.user_auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.bookings import BookingResponse, BookingCreate
from app.usecases.booking import create_booking_usecase

router = APIRouter(prefix="/bookings", tags=["Client Bookings"])

@router.post(
    "", 
    status_code=status.HTTP_201_CREATED,
    response_model=BookingResponse
)
async def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_booking_usecase(
        db=db,
        user_id=current_user.id,
        master_id=data.master_id,
        service_id=data.service_id,
        date=data.date,
        start_time=data.start_time
    )

  
