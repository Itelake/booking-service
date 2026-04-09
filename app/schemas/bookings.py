from datetime import time, date, datetime
from fastapi import Query
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Annotated, List

class BookingCreate(BaseModel):
    service_id: int
    master_id: int
    date: date
    start_time: time
    
class BookingResponse(BaseModel):
    id: int
    service_id: int
    master_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    price_at_booking: int
    discount_percent_applied: int
    final_price: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )
    
class PaginatedBookingResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    limit: int
    offset: int
    
class BookingType(str, Enum):
    future = "future"
    past = "past"
    all = "all"

class MeBookingFilter(BaseModel):
    type: Annotated[BookingType, Query(default=BookingType.future)] = BookingType.future
    
class BookingStatus(str, Enum):
    created = "created"
    confirmed = "confirmed"
    cancelled = "cancelled"
    done = "done"
    
class BookingFilter(BaseModel):
    status: Annotated[BookingStatus | None, Query(default=None)] = None
    date_from: Annotated[datetime | None, Query(default=None)] = None
    date_to: Annotated[datetime | None, Query(default=None)] = None
    master_id: Annotated[int | None, Query(default=None, ge=1)] = None
    service_id: Annotated[int | None, Query(default=None, ge=1)] = None
    user_id: Annotated[int | None, Query(default=None, ge=1)] = None

class Pagination(BaseModel):
    limit: Annotated[int, Query(default=50, ge=1, le=200)] = 50
    offset: Annotated[int, Query(default=0, ge=0)] = 0
