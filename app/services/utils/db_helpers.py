from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Master, Service, MasterService
from app.models.booking import Booking


async def get_master_or_404(db, master_id: int, *, for_update: bool = False) -> Master:
    q = select(Master).where(Master.id == master_id)
    if for_update:
        q = q.with_for_update()
    master = await db.scalar(q)
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Master not found"
        )
    return master


async def get_service_or_404(db: AsyncSession, service_id: int) -> Service:
    service = await db.scalar(select(Service).where(Service.id == service_id))
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return service


async def get_master_service_or_404(
    db: AsyncSession,
    master_id: int,
    service_id: int,
) -> MasterService:
    ms = await db.scalar(
        select(MasterService).where(
            MasterService.master_id == master_id,
            MasterService.service_id == service_id,
        )
    )
    if not ms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master does not provide this service"
        )
    return ms

async def get_booking_or_404(db, booking_id: int, *, for_update: bool = False) -> Booking:
    q = select(Booking).where(Booking.id == booking_id)
    if for_update:
        q = q.with_for_update()
    booking = await db.scalar(q)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found"
        )
    return booking
    
async def get_user_booking_or_404(db, booking_id: int, user_id: int, *, for_update: bool = False) -> Booking:
    q = select(Booking).where(Booking.id == booking_id, Booking.user_id == user_id)
    if for_update:
        q = q.with_for_update()
    booking = await db.scalar(q)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found"
        )
    return booking