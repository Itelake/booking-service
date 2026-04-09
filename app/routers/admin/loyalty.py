from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.loyalty import LoyaltySettings
from app.schemas.loyalty import LoyaltySettingsResponse, LoyaltySettingsUpsert, LoyaltyActiveUpdate
from app.services.loyalty_service import get_settings

router = APIRouter(prefix="/loyalty", tags=["Admin Loyalty"])

@router.put("/settings", response_model=LoyaltySettingsResponse)
async def upsert_loyalty_settings(
    data: LoyaltySettingsUpsert,
    db: AsyncSession = Depends(get_db)
):
    settings_obj = await get_settings(db)
    
    if settings_obj:
        settings_obj.every_n = data.every_n
        settings_obj.percent = data.percent
    else:
        settings_obj = LoyaltySettings(
            every_n=data.every_n,
            percent=data.percent,
            is_active=True
        )
        db.add(settings_obj)
        
    await db.flush()
    await db.refresh(settings_obj)
    return settings_obj

@router.get("/settings", response_model=LoyaltySettingsResponse)
async def get_loyalty_settings(db: AsyncSession = Depends(get_db)):
    setting_obj = await get_settings(db)
    if not setting_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loyalty settings not configured"
        )
    return setting_obj

@router.patch("/settings/active", response_model=LoyaltySettingsResponse)
async def set_loyalty_active(
    data: LoyaltyActiveUpdate,
    db: AsyncSession = Depends(get_db)
):
    settings_obj = await get_settings(db)
    if not settings_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loyalty settings not configured"
        )
    
    settings_obj.is_active = data.is_active
    await db.flush()
    await db.refresh(settings_obj)
    return settings_obj