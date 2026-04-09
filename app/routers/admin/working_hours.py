from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.utils.db_helpers import get_master_or_404
from app.models.master import MasterWorkingHours
from app.schemas.working_hours import WorkingHours, WorkingHoursResponse

router = APIRouter(prefix="/working-hours", tags=["Admin Working Hours"])

@router.post(
    "/{master_id}",
    response_model=WorkingHoursResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_working_hours(
    master_id: int,
    data: WorkingHours,
    db: AsyncSession = Depends(get_db)
):
    await get_master_or_404(db, master_id, for_update=True)
    
    conflict = await db.scalar(
        select(MasterWorkingHours.id).where(
            MasterWorkingHours.master_id == master_id,
            MasterWorkingHours.weekday == data.weekday,
            MasterWorkingHours.start_time < data.end_time,
            MasterWorkingHours.end_time > data.start_time
        )
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Working hours overlap with existing interval"
        )
        
    wh = MasterWorkingHours(
        master_id = master_id,
        weekday = data.weekday,
        start_time = data.start_time,
        end_time = data.end_time
    )
    db.add(wh)
    await db.flush()
    await db.refresh(wh)
    return wh

