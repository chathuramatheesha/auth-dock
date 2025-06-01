from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPublicOut(BaseModel):
    fullname: str
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
