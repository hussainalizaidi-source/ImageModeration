from fastapi import FastAPI
from app.backend.routers import auth, moderator
from app.database.connection import get_db
from app.backend.middlewares import TrackUsageMiddleware 

app = FastAPI()
app.add_middleware(TrackUsageMiddleware)  

@app.on_event("startup")
async def startup_db():
    db = await get_db()
    
    # Create indexes for both collections
    await db.tokens.create_index("token", unique=True)
    await db.usages.create_index("timestamp")
    
    # Create text index for searching
    await db.usages.create_index([("endpoint", "text")])