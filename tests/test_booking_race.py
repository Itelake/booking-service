import pytest
import asyncio

from tests.factories import (
    create_user, create_master, create_service, assign_service,
    add_working_hours, create_booking
)

@pytest.mark.asyncio
async def test_race_confirm_same_booking(client, db):
    user = await create_user(db)
    master = await create_master(db)
    service = await create_service(db)
    await assign_service(db, master, service)
    await add_working_hours(db, master)
    booking = await create_booking(db, user, master, service)

    async def do_confirm():
        return await client.patch(f"/admin/bookings/{booking.id}/confirm")

    # запускаем одновременно
    r1, r2 = await asyncio.gather(do_confirm(), do_confirm())

    codes = sorted([r1.status_code, r2.status_code])
    # ожидаем: один 200, второй 409
    assert codes == [200, 409]