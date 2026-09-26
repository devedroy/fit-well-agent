"""
MemoryManager: Handles all read/write operations to data/memory.json.
This replaces SQLite as the persistence layer for user profile,
conversation history, workout logs, meal logs, and progress tracking.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Resolve the path relative to this file's location so it works
# regardless of where the process is started from.
_DATA_DIR = Path(__file__).parent.parent / "data"
MEMORY_FILE = _DATA_DIR / "memory.json"


def _load() -> dict:
    """Read and return the full memory document."""
    if not MEMORY_FILE.exists():
        reset_memory()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    """Atomically write the memory document back to disk."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MEMORY_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(MEMORY_FILE)


def dump_memory() -> dict:
    """Return the full memory document (public alias for _load)."""
    return _load()


# ──────────────────────────────────────────────
# User Profile
# ──────────────────────────────────────────────

def get_user_profile() -> dict:
    """Return the stored user profile."""
    return _load()["user_profile"]


def update_user_profile(**kwargs) -> dict:
    """
    Update one or more fields in the user profile.

    Accepted keyword arguments match the top-level keys in
    user_profile (name, age, gender, weight_kg, height_cm, goal,
    fitness_level, dietary_restrictions, location).

    Returns the updated profile.
    """
    data = _load()
    profile = data["user_profile"]
    allowed = set(profile.keys()) - {"updated_at"}
    for key, value in kwargs.items():
        if key in allowed:
            profile[key] = value
    profile["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save(data)
    return profile


# ──────────────────────────────────────────────
# Conversation History
# ──────────────────────────────────────────────

def get_conversation_history() -> list:
    """Return all conversation turns."""
    return _load()["conversation_history"]


def append_message(role: str, content: str) -> None:
    """
    Append a single message to the conversation history.

    Args:
        role:    'user' | 'assistant' | 'tool'
        content: The message text.
    """
    data = _load()
    data["conversation_history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save(data)


def clear_conversation_history() -> None:
    """Wipe all conversation history (start a new session)."""
    data = _load()
    data["conversation_history"] = []
    _save(data)


# ──────────────────────────────────────────────
# Workout History
# ──────────────────────────────────────────────

def log_workout(workout_type: str, duration_min: int,
                exercises: list, notes: str = "") -> dict:
    """
    Append a workout session to the workout history.

    Args:
        workout_type:  e.g. 'strength', 'cardio', 'yoga'
        duration_min:  Duration in minutes.
        exercises:     List of dicts [{name, sets, reps, weight_kg}, ...]
        notes:         Optional free-text notes.

    Returns the logged workout entry.
    """
    data = _load()
    entry = {
        "id": len(data["workout_history"]) + 1,
        "date": datetime.now(timezone.utc).isoformat(),
        "type": workout_type,
        "duration_min": duration_min,
        "exercises": exercises,
        "notes": notes,
    }
    data["workout_history"].append(entry)
    _save(data)
    return entry


def get_workout_history(limit: int = 20) -> list:
    """Return the most recent `limit` workout sessions."""
    return _load()["workout_history"][-limit:]


# ──────────────────────────────────────────────
# Meal Logs
# ──────────────────────────────────────────────

def log_meal(meal_type: str, foods: list,
             total_calories: int, macros: dict) -> dict:
    """
    Append a meal entry to the meal log.

    Args:
        meal_type:       'breakfast' | 'lunch' | 'dinner' | 'snack'
        foods:           List of food strings.
        total_calories:  Estimated total calories.
        macros:          {protein_g, carbs_g, fat_g}

    Returns the logged meal entry.
    """
    data = _load()
    entry = {
        "id": len(data["meal_logs"]) + 1,
        "date": datetime.now(timezone.utc).isoformat(),
        "meal_type": meal_type,
        "foods": foods,
        "total_calories": total_calories,
        "macros": macros,
    }
    data["meal_logs"].append(entry)
    _save(data)
    return entry


def get_meal_logs(limit: int = 30) -> list:
    """Return the most recent `limit` meal entries."""
    return _load()["meal_logs"][-limit:]


# ──────────────────────────────────────────────
# Progress Tracking
# ──────────────────────────────────────────────

def log_weight(weight_kg: float) -> dict:
    """Append a body-weight data point."""
    data = _load()
    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "weight_kg": weight_kg,
    }
    data["progress_tracking"]["weight_log"].append(entry)
    _save(data)
    return entry


def log_strength(exercise: str, weight_kg: float,
                 reps: int, sets: int) -> dict:
    """Append a personal-record / strength data point."""
    data = _load()
    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "exercise": exercise,
        "weight_kg": weight_kg,
        "reps": reps,
        "sets": sets,
    }
    data["progress_tracking"]["strength_log"].append(entry)
    _save(data)
    return entry


def log_cardio(activity: str, duration_min: int,
               distance_km: float = None, calories: int = None) -> dict:
    """Append a cardio data point."""
    data = _load()
    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "activity": activity,
        "duration_min": duration_min,
        "distance_km": distance_km,
        "calories": calories,
    }
    data["progress_tracking"]["cardio_log"].append(entry)
    _save(data)
    return entry


def get_progress_tracking() -> dict:
    """Return all progress tracking data."""
    return _load()["progress_tracking"]


# ──────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────

def reset_memory() -> None:
    """
    Reset memory.json to a blank slate.
    Use with caution — this erases all stored data.
    """
    blank = {
        "user_profile": {
            "name": None,
            "age": None,
            "gender": None,
            "weight_kg": None,
            "height_cm": None,
            "goal": None,
            "fitness_level": None,
            "dietary_restrictions": [],
            "location": None,
            "updated_at": None,
        },
        "conversation_history": [],
        "workout_history": [],
        "meal_logs": [],
        "progress_tracking": {
            "weight_log": [],
            "strength_log": [],
            "cardio_log": [],
        },
    }
    _save(blank)
