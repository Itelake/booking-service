from fastapi import APIRouter, Depends
from . import services, bookings, availability, me_bookings, me
from app.auth.user_auth import get_current_user

client_router = APIRouter(
    prefix="/client",
    dependencies=[Depends(get_current_user)]
)

client_router.include_router(services.router)
client_router.include_router(availability.router)
client_router.include_router(bookings.router)
client_router.include_router(me_bookings.router)
client_router.include_router(me.router)