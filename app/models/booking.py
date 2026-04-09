from sqlalchemy import Boolean, Column, Integer, DateTime, String, ForeignKey, func, text
from sqlalchemy.orm import relationship

from .base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False, index=True)
    master_id = Column(Integer, ForeignKey("masters.id", ondelete="RESTRICT"), nullable=False, index=True)

    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False)

    status = Column(String(32), server_default=text("'created'"), nullable=False)
    price_at_booking = Column(Integer, nullable=False)
    discount_percent_applied = Column(Integer, nullable=False, server_default=text("0"))
    final_price = Column(Integer, nullable=False)
    
    reminder_sent_24h = Column(Boolean, default=False)
    reminder_sent_2h = Column(Boolean, default=False)

    reminder_24h_task_id = Column(String, nullable=True)
    reminder_2h_task_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    master = relationship("Master", back_populates="bookings")
