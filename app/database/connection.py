from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def get_db():
    # Connect with admin credentials
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    return client[settings.MONGO_DB]



