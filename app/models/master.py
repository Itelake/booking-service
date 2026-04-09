from sqlalchemy import Column, Index, Integer, Boolean, String, DateTime, ForeignKey, Time, func
from sqlalchemy.orm import relationship

from .base import Base


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True)  # index=True не нужно, PK уже индекс
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=True)
    bio = Column(String(1000), nullable=True)
    phone = Column(String(16), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    services = relationship("MasterService", back_populates="master", cascade="all, delete-orphan")
    working_hours = relationship("MasterWorkingHours", back_populates="master", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="master")


class MasterService(Base):
    __tablename__ = "master_services"

    master_id = Column(Integer, ForeignKey("masters.id", ondelete="CASCADE"), primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    master = relationship("Master", back_populates="services")
    service = relationship("Service", back_populates="masters")

    __table_args__ = (
        Index("ix_master_services_service_id", "service_id"),
    )


class MasterWorkingHours(Base):
    __tablename__ = "master_working_hours"

    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    master = relationship("Master", back_populates="working_hours")

    __table_args__ = (
        Index("ix_mwh_master_weekday", "master_id", "weekday"),
    )
