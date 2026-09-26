"""
Application configuration for FitWell.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fitwell-secret-dev-key-2026")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    USE_DUMMY_MAP_DATA = os.getenv("USE_DUMMY_MAP_DATA", "true").lower() in ("true", "1", "yes")
    DATA_DIR = BASE_DIR / "data"
    MEMORY_FILE = DATA_DIR / "memory.json"
