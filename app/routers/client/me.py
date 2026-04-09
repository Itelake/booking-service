from fastapi import APIRouter, Depends
from app.auth.user_auth import get_current_user
from app.models.user import User
from app.schemas.users import UserMeResponse

router = APIRouter(prefix="/me", tags=["Client Me"])

@router.get("", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
