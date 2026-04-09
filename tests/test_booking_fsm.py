import pytest
from datetime import timedelta

from app.schemas.bookings import BookingStatus
from app.services.utils.time import utc_now
from tests.factories import create_user,create_master,create_service,assign_service,add_working_hours,create_booking

async def make_booking(db):
    user = await create_user(db)
    master = await create_master(db)
    service = await create_service(db)
    await assign_service(db, master, service)
    await add_working_hours(db, master)
    booking = await create_booking(db, user, master, service)
    return booking

@pytest.mark.asyncio
async def test_admin_confirm_success(client, db):
    booking = await make_booking(db)

    response = await client.patch(f"/admin/bookings/{booking.id}/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_admin_done_success_200(client, db):
    booking = await make_booking(db)
    
    booking.status = BookingStatus.confirmed.value
    booking.end_datetime = utc_now() - timedelta(minutes=1)
    await db.flush()
    await db.refresh(booking)
    
    resp = await client.patch(f"/admin/bookings/{booking.id}/done")
    assert resp.status_code == 200
    assert resp.json()["status"] == BookingStatus.done.value
    
@pytest.mark.asyncio
async def test_admin_confirm_in_the_past_400(client, db):
    booking = await make_booking(db)
    
    booking.start_datetime = utc_now() - timedelta(minutes=1)
    await db.flush()
    await db.refresh(booking)
    
    resp = await client.patch(f"/admin/bookings/{booking.id}/confirm")
    assert resp.status_code == 400
    
@pytest.mark.asyncio
async def test_invalid_double_confirm(client, db):
    booking = await make_booking(db)

    await client.patch(f"/admin/bookings/{booking.id}/confirm")
    response = await client.patch(f"/admin/bookings/{booking.id}/confirm")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_done_without_confirm(client, db):
    booking = await make_booking(db)

    response = await client.patch(f"/admin/bookings/{booking.id}/done")
    assert response.status_code == 409
    
@pytest.mark.asyncio
async def test_admin_cancel_success_200(client, db):
    booking = await make_booking(db)
    
    response = await client.patch(f"/admin/bookings/{booking.id}/cancel")
    assert response.status_code == 200    
    
    
@pytest.mark.asyncio
async def test_admin_done_and_cancel(client, db):
    booking = await make_booking(db)
    
    booking.status = BookingStatus.done.value
    await db.flush()
    await db.refresh(booking)
    
    response = await client.patch(f"/admin/bookings/{booking.id}/cancel")
    assert response.status_code == 409
    
@pytest.mark.asyncio
async def test_admin_confirm_not_found_404(client):
    r = await client.patch("/admin/bookings/999999/confirm")
    assert r.status_code == 404
    
@pytest.mark.asyncio
async def test_admin_done_before_end_400(client, db):
    booking = await make_booking(db)

    r1 = await client.patch(f"/admin/bookings/{booking.id}/confirm")
    assert r1.status_code == 200

    r2 = await client.patch(f"/admin/bookings/{booking.id}/done")
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Cannot mark as done before booking ends"
    
@pytest.mark.asyncio
async def test_admin_cancel_after_confirm_success_200(client, db):
    booking = await make_booking(db)

    r1 = await client.patch(f"/admin/bookings/{booking.id}/confirm")
    assert r1.status_code == 200

    r2 = await client.patch(f"/admin/bookings/{booking.id}/cancel")
    assert r2.status_code == 200
    assert r2.json()["status"] == BookingStatus.cancelled.value
    

    

