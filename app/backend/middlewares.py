from fastapi import Request
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from app.database.connection import get_db


class TrackUsageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "authorization" in request.headers:
            token = request.headers["authorization"].split("Bearer ")[-1]
            db = await get_db()
            await db.usages.insert_one(
                {
                    "token": token,
                    "endpoint": request.url.path,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
        return response
