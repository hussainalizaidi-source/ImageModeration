from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from contextlib import asynccontextmanager
import os
from pathlib import Path
import requests
from app.backend.dependencies import get_current_token
from app.config import Settings
from app.database.connection import get_db
from app.backend.middlewares import TrackUsageMiddleware
from app.backend.routers import auth, moderator
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.models import ModerationResult


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

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app = FastAPI(lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)
app.include_router(auth.router)
app.include_router(moderator.router)
app.add_middleware(TrackUsageMiddleware)


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload", include_in_schema=False)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/moderate-ui", include_in_schema=False)
async def moderate_image_ui(
    request: Request,
    file: UploadFile = File(...),
    token: str = Depends(get_current_token)
):
    try:
        # Existing moderation logic from moderator router
        image_bytes = await file.read()
        if len(image_bytes) > 20 * 1024 * 1024:
            raise HTTPException(413, "Image too large (max 20MB)")

        files = {
            'media': (
                file.filename or "image.jpg",
                image_bytes,
                file.content_type or 'image/jpeg'
            )
        }
        settings = Settings()
        headers = {'authorization': f'Bearer {settings.HIVE_API_KEY}'}

        response = requests.post(
            moderator.HIVE_API_URL,
            files=files,
            headers=headers
        )
        if response.status_code != 200:
            raise HTTPException(502, f"Hive API error: {response.text}")

        hive_data = response.json()

        categories = {}
        max_confidence = 0.0
        is_safe = True

        for output in hive_data.get('output', []):
            for class_info in output.get('classes', []):
                class_name = class_info.get('class')
                score = class_info.get('value', 0.0)

                if class_name in moderator.RELEVANT_CATEGORIES:
                    categories[class_name] = score
                    threshold = moderator.SAFETY_THRESHOLDS.get(
                        class_name, 1.0
                    )
                    if score >= threshold:
                        is_safe = False
                        max_confidence = max(max_confidence, score)

        result = ModerationResult(
            is_safe=is_safe,
            categories=categories,
            confidence=max_confidence if not is_safe else 0.0
        )

        return templates.TemplateResponse("result.html", {
            "request": request,
            "result": result,
            "categories": categories,
            "SAFETY_THRESHOLDS": moderator.SAFETY_THRESHOLDS
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"Moderation failed: {str(e)}"
        })
