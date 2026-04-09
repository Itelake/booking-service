import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

class MasterCreate(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str | None = None
    phone: str
    bio: str | None = None
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()

        if not re.fullmatch(r"\+\d{7,15}", v):
            raise ValueError("Phone must be in format +77071234567")

        return v
    
class MasterResponse(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    phone: str
    bio: str | None = None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )

class MasterServiceUpsert(BaseModel):
    price: int
    duration_minutes: int
    
    @field_validator("duration_minutes")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        if v % 15 != 0:
            raise ValueError("Duration must be multiple of 15 minutes")
        return v
    
class MasterServiceResponse(BaseModel):
    master_id: int
    service_id : int
    price: int
    duration_minutes: int
    
    model_config = ConfigDict(
        from_attributes=True
    )