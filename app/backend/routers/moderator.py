from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import requests
from app.config import settings
from app.backend.dependencies import get_current_token
from app.database.models import ModerationResult

router = APIRouter(prefix="/moderate", tags=["Moderation"])
HIVE_API_URL = "https://api.thehive.ai/api/v3/hive/visual-moderation"

SAFETY_THRESHOLDS = {
    # Core NSFW
    "general_nsfw": 0.75,
    "yes_realistic_nsfw": 0.65,
    "yes_undressed": 0.6,

    # Nudity & Sexual Content
    "yes_female_nudity": 0.65,
    "yes_male_nudity": 0.65,
    "yes_sexual_activity": 0.55,
    "yes_sexual_intent": 0.6,
    "yes_genitals": 0.5,
    "yes_breast": 0.55,
    "yes_butt": 0.55,

    # Violence & Weapons
    "violence/graphic": 0.7,
    "gun_in_hand": 0.6,
    "knife_in_hand": 0.65,
    "yes_fight": 0.7,
    "very_bloody": 0.65,
    "human_corpse": 0.5,

    # Self-harm & Dangerous Content
    "yes_self_harm": 0.6,
    "hanging": 0.65,
    "noose": 0.7,
    "yes_pills": 0.7,

    # Hate Symbols & Extremism
    "yes_nazi": 0.8,
    "yes_kkk": 0.8,
    "yes_confederate": 0.8,
    "yes_terrorist": 0.75,

    # Illegal/Regulated Content
    "yes_marijuana": 0.7,
    "yes_animal_abuse": 0.65,
    "illicit_injectables": 0.7,

    # Child Safety
    "yes_child_present": 0.6
}

RELEVANT_CATEGORIES = [
    # Core Moderation
    "general_nsfw", "yes_realistic_nsfw", "yes_undressed",

    # Nudity & Sexual
    "yes_female_nudity", "yes_male_nudity", "yes_sexual_activity",
    "yes_sexual_intent", "yes_genitals", "yes_breast", "yes_butt",

    # Violence
    "violence/graphic", "gun_in_hand", "knife_in_hand", "yes_fight",
    "very_bloody", "human_corpse",

    # Self-harm
    "yes_self_harm", "hanging", "noose", "yes_pills",

    # Hate Groups
    "yes_nazi", "yes_kkk", "yes_confederate", "yes_terrorist",

    # Regulated Content
    "yes_marijuana", "yes_animal_abuse", "illicit_injectables",

    # Child Safety
    "yes_child_present"
]


@router.post("", response_model=ModerationResult)
async def moderate_image(
    file: UploadFile = File(...),
    token: str = Depends(get_current_token)
):
    try:
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
        headers = {'authorization': f'Bearer {settings.HIVE_API_KEY}'}

        response = requests.post(HIVE_API_URL, files=files, headers=headers)
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

                if class_name in RELEVANT_CATEGORIES:
                    categories[class_name] = score
                    threshold = SAFETY_THRESHOLDS.get(class_name, 1.0)

                    if score >= threshold:
                        is_safe = False
                        max_confidence = max(max_confidence, score)

        return ModerationResult(
            is_safe=is_safe,
            categories=categories,
            confidence=max_confidence if not is_safe else 0.0
        )

    except Exception as e:
        raise HTTPException(500, f"Moderation failed: {str(e)}")
