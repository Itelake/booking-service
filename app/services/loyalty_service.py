from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Booking, LoyaltySettings, User

async def calculate_discount_percent(
    db: AsyncSession,
    user_id: int,
) -> int:
    await db.execute(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
    )

    settings = await db.scalar(
        select(LoyaltySettings)
        .where(LoyaltySettings.is_active.is_(True))
    )

    if not settings:
        return 0

    done_count = await db.scalar(
        select(func.count(Booking.id)).where(
            Booking.user_id == user_id,
            Booking.status == "done"
        )
    )

    done_count = int(done_count or 0)
    next_number = done_count + 1

    if settings.every_n > 0 and next_number % settings.every_n == 0:
        return int(settings.percent)

    return 0

async def get_settings(db: AsyncSession) -> LoyaltySettings | None:
    return await db.scalar(
        select(LoyaltySettings).order_by(LoyaltySettings.id.desc()).limit(1)
    )