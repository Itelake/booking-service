from zoneinfo import ZoneInfo
from app.database import SessionLocal
from app.models.booking import Booking
from app.models.user import User
from app.tasks.celery_app import celery_app
from app.tasks.utils import send_telegram_message, logger
from sqlalchemy.orm import joinedload

ALMATY_TZ = ZoneInfo("Asia/Almaty")

@celery_app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_booking_created_notification(booking_id: int):
    logger.info(f"Start send_booking_created_notification: booking_id={booking_id}")
    db = SessionLocal()
    try:
        booking = db.query(Booking)\
            .options(
                joinedload(Booking.user),
                joinedload(Booking.master),
                joinedload(Booking.service)
            )\
            .filter(Booking.id == booking_id)\
            .first()

        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            return

        user = booking.user
        master = booking.master
        service = booking.service
        
        start_local = booking.start_datetime.astimezone(ALMATY_TZ)
        
        message = (
            f"📅 Новая запись\n\n"
            f"Клиент: {user.username}\n"
            f"Мастер: {master.first_name} {master.last_name}\n"
            f"Услуга: {service.name}\n\n"
            f"Дата: {start_local.strftime('%d.%m.%Y')}\n"
            f"Время: {start_local.strftime('%H:%M')}"
        )

        admins = db.query(User).filter(User.is_admin == True).all()

        for admin in admins:
            if admin.telegram_id:
                send_telegram_message(admin.telegram_id, message)

    finally:
        db.close()


@celery_app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_booking_reminder(booking_id: int, reminder_type: str):
    logger.info(f"Start send_booking_reminder: booking_id={booking_id}, type={reminder_type}")
    db = SessionLocal()
    try:
        booking = db.query(Booking)\
            .options(joinedload(Booking.user))\
            .filter(
                Booking.id == booking_id,
                Booking.status.in_(["created", "confirmed"])
            )\
            .first()
            
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            return

        if reminder_type == "24h":
            if booking.reminder_sent_24h:
                logger.info(f"24h reminder already sent for booking {booking_id}")
                return
        elif reminder_type == "2h":
            if booking.reminder_sent_2h:
                logger.info(f"2h reminder already sent for booking {booking_id}")
                return
        else:
            return

        user = booking.user
        if not user.telegram_id:
            return

        start_local = booking.start_datetime.astimezone(ALMATY_TZ)

        message = (
            f"⏰ Напоминание\n"
            f"Дата: {start_local.strftime('%d.%m.%Y')}\n"
            f"Время: {start_local.strftime('%H:%M')}"
        )

        send_telegram_message(user.telegram_id, message)

        if reminder_type == "24h":
            booking.reminder_sent_24h = True
        elif reminder_type == "2h":
            booking.reminder_sent_2h = True

        db.commit()
        logger.info(f"Reminder sent: booking_id={booking_id}, type={reminder_type}")
    finally:
        db.close()
        

@celery_app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True)
def send_mass_message(text: str):
    logger.info("Start mass mailing")
    
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.telegram_id.isnot(None)
        ).all()
        
        for user in users:
            try:
                send_telegram_message(user.telegram_id, text)
            except Exception as e:
                logger.error(f"Ошибка отправки {user.telegram_id}: {e}")
    
    finally:
        db.close()
        
@celery_app.task
def notify_admins(booking_id: int):
    db = SessionLocal()
    try:
        booking = db.query(Booking).options(
            joinedload(Booking.user),
            joinedload(Booking.master),
            joinedload(Booking.service)
        ).filter(Booking.id == booking_id).first()

        if not booking:
            return

        message = (
            f"❌ Запись отменена\n\n"
            f"Клиент: {booking.user.username}\n"
            f"Мастер: {booking.master.first_name}\n"
            f"Услуга: {booking.service.name}"
        )

        admins = db.query(User).filter(User.is_admin == True).all()

        for admin in admins:
            if admin.telegram_id:
                send_telegram_message(admin.telegram_id, message)
    finally:
        db.close()