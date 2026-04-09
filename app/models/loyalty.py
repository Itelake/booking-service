from sqlalchemy import Column, Integer, Boolean, DateTime, func, text

from .base import Base

class LoyaltySettings(Base):
    __tablename__ = "loyalty_settings"

    id = Column(Integer, primary_key=True)
    every_n = Column(Integer, nullable=False)
    percent = Column(Integer, nullable=False)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
