from fastapi import APIRouter, Depends

from app.auth.user_auth import require_admin
from . import bookings, loyalty, masters, services, working_hours, notifications

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]
)

admin_router.include_router(working_hours.router)
admin_router.include_router(masters.router)
admin_router.include_router(services.router)
admin_router.include_router(loyalty.router)
admin_router.include_router(bookings.router)
admin_router.include_router(notifications.router)

