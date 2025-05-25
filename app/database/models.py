from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

class TokenCreate(BaseModel):
    is_admin: bool = False

class TokenInDB(BaseModel):
    token: str
    is_admin: bool
    created_at: datetime = datetime.now(timezone.utc)

class UsageRecord(BaseModel):
    token: str
    endpoint: str
    timestamp: datetime

class ModerationRequest(BaseModel):
    image_url: str
    user_comment: Optional[str] = None

class ModerationResult(BaseModel):
    is_safe: bool
    categories: dict
    confidence: float