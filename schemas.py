from datetime import datetime
from pydantic import BaseModel, EmailStr


class SubscriberCreate(BaseModel):
    email: EmailStr


class SubscriberResponse(BaseModel):
    id: int
    email: EmailStr
    is_subscribed: bool

    class Config:
        from_attributes = True


class SubscriberListResponse(BaseModel):
    id: int
    email: EmailStr
    is_subscribed: bool
    created_at: datetime

    class Config:
        from_attributes = True