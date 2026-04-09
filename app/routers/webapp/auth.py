import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, AuthToken
from app.schemas.webapp_auth import WebAppAuthRequest, WebAppAuthResponse
from app.auth.webapp_auth import verify_telegram_webapp_init_data
from app.config import settings

router = APIRouter(prefix="/webapp", tags=["WebApp"])

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

@router.post("/auth", response_model=WebAppAuthResponse, status_code=status.HTTP_201_CREATED)
async def webapp_auth(payload: WebAppAuthRequest, db: AsyncSession = Depends(get_db)):
    data = verify_telegram_webapp_init_data(payload.init_data)

    user_raw = data.get("user")
    if not user_raw:
        raise HTTPException(status_code=401, detail="Telegram 'user' not found in initData")

    user_obj = json.loads(user_raw)
    telegram_id = int(user_obj["id"])
    username = user_obj.get("username")

    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            is_active=True,
            is_admin=False,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        if username and username != user.username:
            user.username = username
            await db.flush()
            await db.refresh(user)

    ttl_hours = settings.TOKEN_TTL_HOURS
    token_value = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(hours=ttl_hours)

    token = AuthToken(
        user_id=user.id,
        access_token=token_value,
        expires_at=expires_at,
    )
    db.add(token)
    await db.flush()

    return WebAppAuthResponse(access_token=token_value, expires_at=expires_at)
