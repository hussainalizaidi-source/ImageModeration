from app.database.models import TokenInDB
import secrets


class TokenCRUD:
    @staticmethod
    async def create_token(db, is_admin: bool):
        token = secrets.token_urlsafe(32)
        token_data = TokenInDB(token=token, is_admin=is_admin)
        await db.tokens.insert_one(token_data.dict())
        return token

    @staticmethod
    async def token_exists(db, token: str):
        return await db.tokens.find_one({"token": token})

    @staticmethod
    async def is_admin(db, token: str):
        result = await db.tokens.find_one({"token": token})
        return result.get("is_admin") if result else False

    @staticmethod
    async def list_tokens(db):
        return await db.tokens.find().to_list(None)

    @staticmethod
    async def revoke_token(db, token: str):
        return await db.tokens.delete_one({"token": token})
