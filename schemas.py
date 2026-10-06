from datetime import datetime
from typing import Literal

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

class FeedbackCreate(BaseModel):
    email: EmailStr
    rating: Literal["비싸다", "적당하다", "저렴하다", "기타"]


class FeedbackResponse(BaseModel):
    id: int
    email: EmailStr
    rating: str
    created_at: datetime

    class Config:
        from_attributes = True