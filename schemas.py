from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator


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
    email: Optional[EmailStr] = None
    rating: Literal["비싸다", "적당하다", "저렴하다", "기타"]

    @field_validator("email", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        # 프론트가 "" (빈 문자열)을 보내도 에러 없이 None으로 처리
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v



class FeedbackResponse(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    rating: str
    created_at: datetime

    class Config:
        from_attributes = True