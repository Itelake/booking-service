from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.master import MasterWorkingHours
from app.models.booking import Booking
from app.schemas.availability import AvailabilityRequest, AvailabilityResponse
from app.services.utils.db_helpers import get_master_or_404, get_service_or_404, get_master_service_or_404
from app.services.utils.time import overlaps

router = APIRouter(prefix="/availability", tags=["Client Availability"])

ALMATY_TZ = ZoneInfo("Asia/Almaty")
UTC = ZoneInfo("UTC")

@router.post("", response_model=AvailabilityResponse)
async def get_availability(
    data: AvailabilityRequest,
    db: AsyncSession = Depends(get_db),
):
    await get_master_or_404(db, data.master_id)
    await get_service_or_404(db, data.service_id)
    ms = await get_master_service_or_404(db, data.master_id, data.service_id)

    working_hours = await db.scalar(
        select(MasterWorkingHours).where(
            MasterWorkingHours.master_id == data.master_id,
            MasterWorkingHours.weekday == data.date.weekday(),
        )
    )
    if not working_hours:
        return AvailabilityResponse(
            date=data.date,
            service_id=data.service_id,
            master_id=data.master_id,
            slots=[],
        )

    step = timedelta(minutes=ms.duration_minutes)

    day_start_local = datetime.combine(data.date, working_hours.start_time, tzinfo=ALMATY_TZ)
    day_end_local = datetime.combine(data.date, working_hours.end_time, tzinfo=ALMATY_TZ)

    day_start_utc = day_start_local.astimezone(UTC)
    day_end_utc = day_end_local.astimezone(UTC)

    busy_rows = (await db.execute(
        select(Booking.start_datetime, Booking.end_datetime).where(
            Booking.master_id == data.master_id,
            Booking.status.in_(("created", "confirmed")),
            Booking.start_datetime < day_end_utc,
            Booking.end_datetime > day_start_utc,
        )
    )).all()

    slots: list[time] = []
    current_local = day_start_local

    while current_local + step <= day_end_local:
        slot_start_utc = current_local.astimezone(UTC)
        slot_end_utc = (current_local + step).astimezone(UTC)

        has_conflict = False
        for (b_start, b_end) in busy_rows:
            if overlaps(slot_start_utc, slot_end_utc, b_start, b_end):
                has_conflict = True
                break

        if not has_conflict:
            slots.append(current_local.time())

        current_local += step

    return AvailabilityResponse(
        date=data.date,
        service_id=data.service_id,
        master_id=data.master_id,
        slots=slots,
    )
