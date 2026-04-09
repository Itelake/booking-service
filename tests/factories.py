import itertools
from zoneinfo import ZoneInfo
from app.models import User, Master, Service, MasterService, MasterWorkingHours, Booking
from datetime import datetime, time, timedelta

from app.schemas.bookings import BookingStatus

_telegram_seq = itertools.count(100000000)
_master_seq = itertools.count(1)
ALMATY_TZ = ZoneInfo("Asia/Almaty")

async def create_user(db, *, is_admin=False):
    tid = next(_telegram_seq)

    user = User(
        telegram_id=tid,
        username=f"user_{tid}",
        is_active=True,
        is_admin=is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_master(db):
    n = next(_master_seq)
    master = Master(
        first_name=f"TestMaster{n}",
        last_name="Lastname",
        phone=f"+7700{n:07d}",
        bio="Test bio",
        is_active=True,
    )
    db.add(master)
    await db.commit()
    await db.refresh(master)
    return master


async def create_service(db):
    service = Service(name="Test Service")
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def assign_service(db, master, service, *, duration_minutes=60, price=1000):
    ms = MasterService(
        master_id=master.id,
        service_id=service.id,
        duration_minutes=duration_minutes,
        price=price,
    )
    db.add(ms)
    await db.commit()
    await db.refresh(ms)
    return ms


async def add_working_hours(db, master):
    wh = MasterWorkingHours(
        master_id=master.id,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    db.add(wh)
    await db.commit()
    return wh


async def create_booking(db, user, master, service):
    start_dt = (
    datetime.now(ALMATY_TZ).replace(hour=10, minute=0, second=0, microsecond=0)
    + timedelta(days=1)
)
    end_dt = start_dt + timedelta(minutes=60)

    booking = Booking(
        user_id=user.id,
        master_id=master.id,
        service_id=service.id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status=BookingStatus.created.value,
        price_at_booking=1000,  
        final_price=1000,        
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking