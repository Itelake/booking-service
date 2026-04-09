from datetime import datetime
from pydantic import BaseModel

class WebAppAuthRequest(BaseModel):
    init_data: str
    
class WebAppAuthResponse(BaseModel):
    access_token: str
    expires_at: datetime