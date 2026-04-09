from .base import Base

# Импортируем модели, чтобы они зарегистрировались в metadata
from .user import User, AuthToken
from .service import Service, ServicePhoto
from .master import Master, MasterService, MasterWorkingHours
from .booking import Booking
from .loyalty import LoyaltySettings

__all__ = [
    "Base",
    "User", "AuthToken",
    "Service", "ServicePhoto",
    "Master", "MasterService", "MasterWorkingHours",
    "Booking",
    "LoyaltySettings",
]
