from datetime import time
from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkingHours(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    
    @model_validator(mode="after")
    def validate_time_order(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be less than end_time")
        return self
    
class WorkingHoursResponse(BaseModel):
    id: int
    master_id: int
    weekday: int
    start_time: time
    end_time: time

    model_config = ConfigDict(
        from_attributes=True
    )