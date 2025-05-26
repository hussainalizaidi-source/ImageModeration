from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.connection import get_db
from app.backend.middlewares import TrackUsageMiddleware
from app.backend.routers import auth, moderator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    db = await get_db()
    # Create indexes for both collections
    await db.tokens.create_index("token", unique=True)
    await db.usages.create_index("timestamp")
    await db.usages.create_index([("endpoint", "text")])

    yield  # Application runs during this period

    # Optional: Add any shutdown logic here if needed


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(moderator.router)
app.add_middleware(TrackUsageMiddleware)
