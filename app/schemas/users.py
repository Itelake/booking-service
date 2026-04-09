from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserMeResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )