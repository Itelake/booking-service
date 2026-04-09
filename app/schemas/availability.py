from datetime import time, date
from pydantic import BaseModel

class AvailabilityRequest(BaseModel):
    service_id: int
    master_id: int
    date: date
    
class AvailabilityResponse(BaseModel):
    date: date
    service_id: int
    master_id: int
    slots: list[time]