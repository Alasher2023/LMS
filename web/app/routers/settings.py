from fastapi import APIRouter, Body
from pydantic import BaseModel
import json
import os

router = APIRouter(
    tags=["settings"],
    prefix="/settings",
)

# For simplicity, we'll store settings in a JSON file.
SETTINGS_FILE = "settings.json"

class Settings(BaseModel):
    wrong_question_storage_path: str

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_settings(settings: dict):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

@router.post("/wrong_question_path")
def save_wrong_question_path(settings: Settings):
    current_settings = load_settings()
    current_settings['wrong_question_storage_path'] = settings.wrong_question_storage_path
    save_settings(current_settings)
    return {"message": "Settings saved successfully."}

@router.get("/wrong_question_path")
def get_wrong_question_path():
    settings = load_settings()
    return {"path": settings.get('wrong_question_storage_path')}
