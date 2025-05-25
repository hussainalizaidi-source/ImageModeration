from fastapi import APIRouter, Depends, UploadFile, File
from app.backend.dependencies import get_current_token
from app.database.models import ModerationResult

router = APIRouter(prefix="/moderate", tags=["Moderation"])


@router.post("", response_model=ModerationResult)
async def moderate_image(
    file: UploadFile = File(...),
    token: str = Depends(get_current_token)
):
    # Placeholder for actual moderation logic
    return {
        "is_safe": True,
        "categories": {},
        "confidence": 0.95
    }
