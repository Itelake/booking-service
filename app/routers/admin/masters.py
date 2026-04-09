from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

from app.database import get_db
from app.schemas.masters import MasterCreate, MasterResponse, MasterServiceResponse, MasterServiceUpsert
from app.models.master import Master, MasterService
from app.services.utils.db_helpers import get_master_or_404, get_service_or_404

router = APIRouter(prefix="/masters", tags=["Admin Masters"])

@router.post(
    "",
    response_model=MasterResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_master(
    data: MasterCreate,
    db: AsyncSession = Depends(get_db)
):
    master = Master(
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip() if data.last_name else None,
        phone=data.phone.strip(),
        bio=data.bio
    )
    db.add(master)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Master with this phone already exists"
        )

    await db.refresh(master)
    return master

@router.put(
    "/{master_id}/services/{service_id}", 
    response_model=MasterServiceResponse
)
async def assign_service_to_master(
    master_id: int,
    service_id: int,
    data: MasterServiceUpsert,
    db: AsyncSession = Depends(get_db)
):
    await get_master_or_404(db, master_id)
    await get_service_or_404(db, service_id)
        
    stmt = (
        insert(MasterService)
        .values(
            master_id=master_id,
            service_id=service_id,
            price=data.price,
            duration_minutes=data.duration_minutes,
        )
        .on_conflict_do_update(
            index_elements=["master_id", "service_id"],
            set_={"price": data.price, "duration_minutes": data.duration_minutes}
        )
        .returning(MasterService)
    )

    res = await db.execute(stmt)
    link = res.scalar_one()
    await db.flush()
    await db.refresh(link)
    return link
    