from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.crud import TokenCRUD
from app.database.connection import get_db

security = HTTPBearer()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    token = credentials.credentials
    if not await TokenCRUD.token_exists(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    # Update last used timestamp
    await db.tokens.update_one(
        {"token": token},
        {"$set": {"last_used": datetime.now(timezone.now)}}
    )
    return token


async def require_admin(
    token: str = Depends(get_current_token),
    db=Depends(get_db)
):
    if not await TokenCRUD.is_admin(db, token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return token
