from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.database.models import TokenResponse, UsageRecord  # TokenCreate
from app.database.crud import TokenCRUD
from app.backend.dependencies import get_current_token, require_admin
from app.database.connection import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="app/templates")


# @router.post("/tokens", response_model=TokenResponse)
# async def create_token(
#     payload: TokenCreate,
#     admin: dict = Depends(require_admin),
#     db=Depends(get_db)
# ):
#     try:
#         token_doc = await TokenCRUD.create_token(db, payload.is_admin)
#         if not token_doc:
#             raise HTTPException(
#                 status_code=500, detail="Token creation failed"
#             )
#         return TokenResponse(**token_doc)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Token creation failed: {str(e)}"
#         )


@router.post("/logout", include_in_schema=False)
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@router.get("/tokens/new", include_in_schema=False)
async def new_token_form(
    request: Request,
    admin: str = Depends(require_admin)  # Add admin dependency
):
    return templates.TemplateResponse(
        "generate_token.html",
        {"request": request}
    )


@router.post("/tokens", include_in_schema=False)
async def generate_token_ui(
    request: Request,
    is_admin: str = Form("false"),  # Get as string
    token: str = Depends(get_current_token),
    db=Depends(get_db)
):
    # Convert string to boolean
    is_admin_bool = is_admin.lower() == "true"

    # Verify admin status
    is_admin_user = await TokenCRUD.check_admin_status(db, token)
    if not is_admin_user:
        raise HTTPException(
            status_code=403, detail="Admin privileges required"
        )

    token_doc = await TokenCRUD.create_token(db, is_admin_bool)
    return templates.TemplateResponse("token_display.html", {
        "request": request,
        "token": token_doc["token"]
    })


@router.post("/login", include_in_schema=False)
async def ui_login(
    request: Request,
    token: str = Form(...),
    db=Depends(get_db)
):
    valid_token = await TokenCRUD.get_token(db, token)
    if not valid_token:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Invalid token"
        })

    response = RedirectResponse(url="/upload", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}")
    return response


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


@router.get("/usages/{token}", response_model=list[UsageRecord])
async def get_usage(
    token: str,
    admin: dict = Depends(require_admin),
    db=Depends(get_db)
):
    cursor = db.usages.find({"token": token})
    return [UsageRecord(**doc) async for doc in cursor]
