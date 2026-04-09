import pytest
from fastapi import HTTPException
from datetime import date, time, timedelta
from zoneinfo import ZoneInfo

from tests.factories import (
    create_user, create_master, create_service,
    assign_service, add_working_hours
)
from app.services.booking_service import create_booking_core

ALMATY_TZ = ZoneInfo("Asia/Almaty")

def next_weekday_strict_future(d: date, target_weekday: int) -> date:
    days_ahead = (target_weekday - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return d + timedelta(days=days_ahead)

async def setup_booking_context(db):
    user = await create_user(db)
    master = await create_master(db)
    service = await create_service(db)
    await assign_service(db, master, service, duration_minutes=60, price=1000)
    await add_working_hours(db, master)  
    booking_day = next_weekday_strict_future(date.today(), 1)
    return user, master, service, booking_day

@pytest.mark.asyncio
async def test_create_booking_core_ok(db):
    user, master, service, booking_day = await setup_booking_context(db)

    booking = await create_booking_core(
        db=db,
        user_id=user.id,
        master_id=master.id,
        service_id=service.id,
        date=booking_day,
        start_time=time(10, 0),
    )

    assert booking.id is not None
    assert booking.status == "created"
    
    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=booking_day,
            start_time=time(10, 0),
        )

    assert e.value.status_code == 409
    assert e.value.detail == "Time slot is already booked"
    

@pytest.mark.asyncio
async def test_create_booking_core_outside_working_hours_409(db):
    user, master, service, booking_day = await setup_booking_context(db)

    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=booking_day,
            start_time=time(8, 0),
        )

    assert e.value.status_code == 409
    assert e.value.detail == "Booking time is outside master's working hours"
    
    
@pytest.mark.asyncio
async def test_create_booking_core_not_aligned_400(db):
    user, master, service, booking_day = await setup_booking_context(db)

    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=booking_day,
            start_time=time(10, 30),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "start_datetime must align with service duration slots"
    
@pytest.mark.asyncio
async def test_create_booking_core_end_after_working_hours_409(db):
    user, master, service, booking_day = await setup_booking_context(db)

    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=booking_day,
            start_time=time(17, 30),
        )

    assert e.value.status_code == 409
    assert e.value.detail == "Booking time is outside master's working hours"
    
@pytest.mark.asyncio
async def test_create_booking_core_master_not_working_that_day_409(db):
    user, master, service, _  = await setup_booking_context(db)

    wrong_day = next_weekday_strict_future(date.today(), 2)
    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=wrong_day,
            start_time=time(10, 0),
        )

    assert e.value.status_code == 409
    assert e.value.detail == "Master does not work on this day"
    
@pytest.mark.asyncio
async def test_create_booking_core_past_date_400(db):
    user, master, service, _ = await setup_booking_context(db)

    past_day = date.today() - timedelta(days=1)
    with pytest.raises(HTTPException) as e:
        await create_booking_core(
            db=db,
            user_id=user.id,
            master_id=master.id,
            service_id=service.id,
            date=past_day,
            start_time=time(10, 0),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "Cannot create booking in the past"