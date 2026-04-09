from datetime import datetime
from pydantic import AnyUrl, BaseModel, ConfigDict

class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    
class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )

class ServiceMasterResponse(BaseModel):
    master_id: int
    first_name: str
    last_name: str
    bio: str | None = None
    price: int
    duration_minutes: int

    model_config = ConfigDict(
        from_attributes=True
    )
    
class ServicePhotoCreate(BaseModel):
    url: AnyUrl

class ServicePhotoResponse(BaseModel):
    id: int
    service_id: int
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ServicePhotoUpdate(BaseModel):
    url: AnyUrl