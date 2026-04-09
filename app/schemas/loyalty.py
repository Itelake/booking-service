from pydantic import BaseModel, Field, ConfigDict

class LoyaltySettingsUpsert(BaseModel):
    every_n: int = Field(ge=1, le=1000)
    percent: int = Field(ge=0, le=100)

class LoyaltySettingsResponse(BaseModel):
    id: int
    every_n: int
    percent: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class LoyaltyActiveUpdate(BaseModel):
    is_active: bool