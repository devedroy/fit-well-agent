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
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    USE_DUMMY_MAP_DATA = os.getenv("USE_DUMMY_MAP_DATA", "true").lower() in ("true", "1", "yes")
    DATA_DIR = BASE_DIR / "data"
    MEMORY_FILE = DATA_DIR / "memory.json"
