from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.service import Service
from app.models.master import Master, MasterService
from app.schemas.services import ServiceResponse, ServiceMasterResponse
from app.services.utils.db_helpers import get_service_or_404

router = APIRouter(prefix="/services", tags=["Client Services"])

# --------------------
# Получение всех услуг
# --------------------
@router.get("", response_model=list[ServiceResponse])
async def list_services(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Service).where(Service.is_active.is_(True)))
    return result.all()

# --------------------
# Получение мастеров, которые делают данную услугу
# --------------------
@router.get("/{service_id}/masters", response_model=list[ServiceMasterResponse])
async def get_masters_for_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    await get_service_or_404(db, service_id)
    
    q = await db.execute(
        select(Master, MasterService.price, MasterService.duration_minutes)
        .join(MasterService, MasterService.master_id == Master.id)
        .where(
            MasterService.service_id == service_id,
            Master.is_active.is_(True)
            )
        .order_by(Master.first_name.asc(), Master.last_name.asc(), Master.id.asc())
        )
        
    rows = q.all()
    
    return [
        ServiceMasterResponse(
            master_id=m.id,
            first_name=m.first_name,
            last_name=m.last_name,
            bio=m.bio,
            price=price,
            duration_minutes=duration,
        )
        for (m, price, duration) in rows
    ]
    
    
