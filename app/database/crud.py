from datetime import datetime, timezone
import secrets


class TokenCRUD:
    @staticmethod
    async def create_token(db, is_admin: bool) -> dict:
        token = secrets.token_urlsafe(32)
        token_data = {
            "token": token,
            "is_admin": is_admin,
            "created_at": datetime.now(timezone.utc)
        }
        result = await db.tokens.insert_one(token_data)
        # Return document with string ID
        doc = await db.tokens.find_one({"_id": result.inserted_id})
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        return doc

    @staticmethod
    async def get_token(db, token: str):
        doc = await db.tokens.find_one({"token": token})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    async def check_admin_status(db, token: str) -> bool:
        """Check if a token has admin privileges"""
        doc = await db.tokens.find_one({"token": token}, {"is_admin": 1})
        return doc.get("is_admin", False) if doc else False

    @staticmethod
    async def list_tokens(db):
        cursor = db.tokens.find()
        return [TokenCRUD.serialize_token(t) async for t in cursor]

    @staticmethod
    async def revoke_token(db, token: str):
        return await db.tokens.delete_one({"token": token})

    @staticmethod
    def serialize_token(token_doc):
        if token_doc:
            token_doc["_id"] = str(token_doc["_id"])
        return token_doc
