from pydantic import BaseModel

class TokenCreate(BaseModel):
    telegram_id: int
    username: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: str