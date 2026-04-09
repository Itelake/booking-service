from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas.services import ServiceCreate, ServicePhotoResponse, ServiceResponse, ServicePhotoCreate, ServicePhotoUpdate
from app.models.service import Service, ServicePhoto
from app.services.utils.db_helpers import get_service_or_404

router = APIRouter(prefix="/services",tags=["Admin Services"])

@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_service(
    data: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    name = data.name.strip()
    
    service = Service(
        name = name,
        description = data.description,
    )

    db.add(service)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service with this name already exists"
        )

    await db.refresh(service)
    return service

@router.get("/{service_id}/photos", response_model=list[ServicePhotoResponse])
async def list_service_photos(service_id: int, db: AsyncSession = Depends(get_db)):
    await get_service_or_404(db, service_id)
    
    q = select(ServicePhoto).where(ServicePhoto.service_id == service_id).order_by(ServicePhoto.created_at.desc())
    return (await db.scalars(q)).all()

@router.post(
    "/{service_id}/photos",
    response_model=ServicePhotoResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_service_photo(
    service_id: int, 
    data: ServicePhotoCreate, 
    db: AsyncSession = Depends(get_db)
):
    await get_service_or_404(db, service_id)
    
    photo = ServicePhoto(service_id=service_id, url=str(data.url))
    db.add(photo)
    await db.flush()
    await db.refresh(photo)
    return photo

@router.delete("/{service_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_photo(
    service_id: int, 
    photo_id: int, 
    db: AsyncSession = Depends(get_db)
):
    await get_service_or_404(db, service_id)
    
    photo = await db.get(ServicePhoto, photo_id)
    if not photo or photo.service_id != service_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Photo not found"
        )
    
    await db.delete(photo)
    await db.flush()
    return None


@router.patch("/{service_id}/photos/{photo_id}",response_model=ServicePhotoResponse)
async def update_service_photo(
    service_id: int,
    photo_id: int,
    data: ServicePhotoUpdate, 
    db: AsyncSession = Depends(get_db),
):
    await get_service_or_404(db, service_id)

    photo = await db.get(ServicePhoto, photo_id)
    if not photo or photo.service_id != service_id:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo.url = str(data.url)
    await db.flush()
    await db.refresh(photo)
    return photo