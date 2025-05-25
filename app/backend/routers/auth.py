from fastapi import APIRouter, Depends
from app.database.crud import TokenCRUD
from app.backend.dependencies import require_admin
from app.database.connection import get_db
from app.database.models import TokenCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/tokens", dependencies=[Depends(require_admin)])
async def create_token(payload: TokenCreate, db=Depends(get_db)):
    return {"token": await TokenCRUD.create_token(db, payload.is_admin)}


@router.get("/tokens", dependencies=[Depends(require_admin)])
async def list_tokens(db=Depends(get_db)):
    return await TokenCRUD.list_tokens(db)


@router.delete("/tokens/{token}", dependencies=[Depends(require_admin)])
async def revoke_token(token: str, db=Depends(get_db)):
    await TokenCRUD.revoke_token(db, token)
    return {"message": "Token revoked"}
