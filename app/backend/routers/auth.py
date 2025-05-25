from fastapi import APIRouter, Depends, HTTPException
from app.database.models import TokenCreate, TokenResponse
from app.database.crud import TokenCRUD
from app.backend.dependencies import require_admin
from app.database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/tokens", response_model=TokenResponse)
async def create_token(
    payload: TokenCreate,
    admin: dict = Depends(require_admin),
    db=Depends(get_db)
):
    try:
        token_doc = await TokenCRUD.create_token(db, payload.is_admin)
        if not token_doc:
            raise HTTPException(
                status_code=500, detail="Token creation failed"
            )
        return TokenResponse(**token_doc)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token creation failed: {str(e)}"
        )


@router.get("/tokens", response_model=list[TokenResponse])
async def list_tokens(
    admin: str = Depends(require_admin),
    db=Depends(get_db)
):
    return await TokenCRUD.list_tokens(db)


@router.delete("/tokens/{token}")
async def revoke_token(
    token: str,
    admin: str = Depends(require_admin),
    db=Depends(get_db)
):
    result = await TokenCRUD.revoke_token(db, token)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"message": "Token revoked successfully"}
