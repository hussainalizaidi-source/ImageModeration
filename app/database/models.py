from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone
from typing import Optional


class TokenBase(BaseModel):
    token: str
    is_admin: bool
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TokenResponse(BaseModel):
    id: str = Field(alias="_id")
    token: str
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )

    @field_validator("id", mode="before")
    def convert_objectid(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value


class TokenCreate(BaseModel):
    is_admin: bool = False


class UsageRecord(BaseModel):
    token: str
    endpoint: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ModerationRequest(BaseModel):
    image_url: str
    user_comment: Optional[str] = None


class ModerationResult(BaseModel):
    is_safe: bool
    categories: dict
    confidence: float
