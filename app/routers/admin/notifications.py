from fastapi import APIRouter
from app.tasks.notification_tasks import send_mass_message

router = APIRouter(tags=["Admin Notifications"])

@router.post("/send")
async def send_message(text: str):
    send_mass_message.delay(text)
    return {"status": "mass mailing started"}