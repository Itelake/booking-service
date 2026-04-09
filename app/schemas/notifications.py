from pydantic import BaseModel


class MassMessage(BaseModel):
    text: str