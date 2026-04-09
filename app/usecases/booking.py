from datetime import timedelta

from app.services.booking_service import cancel_booking_user, create_booking_core
from app.tasks.notification_tasks import (
    notify_admins,
    send_booking_created_notification,
    send_booking_reminder
)
from app.services.utils.time import utc_now


async def create_booking_usecase(
    db,
    user_id,
    master_id,
    service_id,
    date,
    start_time
):
    booking = await create_booking_core(
        db=db,
        user_id=user_id,
        master_id=master_id,
        service_id=service_id,
        date=date,
        start_time=start_time
    )
    await db.commit()

    send_booking_created_notification.delay(booking.id)

    eta_24 = booking.start_datetime - timedelta(hours=24)
    if eta_24 > utc_now():
        result_24 = send_booking_reminder.apply_async(
            args=[booking.id, "24h"],
            eta=eta_24
        )
        booking.reminder_24h_task_id = result_24.id

    eta_2 = booking.start_datetime - timedelta(hours=2)
    if eta_2 > utc_now():
        result_2 = send_booking_reminder.apply_async(
            args=[booking.id, "2h"],
            eta=eta_2
        )
        booking.reminder_2h_task_id = result_2.id

    return booking

async def cancel_booking_usecase(
    db, 
    booking_id, 
    user_id
):
    booking = await cancel_booking_user(
    db=db, 
    booking_id=booking_id, 
    user_id=user_id
    )
    
    await db.commit()
    
    notify_admins.delay(booking.id)
    
    return booking