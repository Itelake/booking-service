from fastapi import APIRouter
from app.schemas.notifications import MassMessage
from app.tasks.notification_tasks import send_mass_message

router = APIRouter(prefix="/notifications", tags=["Admin Notifications"])

@router.post("/send")
async def send_message(message: MassMessage):
    send_mass_message.delay(message.text)
    return {"status": "mass mailing started"}