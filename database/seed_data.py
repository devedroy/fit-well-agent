"""
seed_data.py — Populate data/memory.json with realistic starter data.

Run once before first launch to pre-fill the profile and history so
the agent has context from the first conversation:

    python -m database.seed_data

Safe to re-run: prompts before overwriting existing data.
"""

import sys
from pathlib import Path

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import (
    dump_memory,
    update_user_profile,
    log_workout,
    log_meal,
    log_weight,
    log_cardio,
    reset_memory,
)


SEED_PROFILE = {
    "name": "Devpreyo",
    "age": 25,
    "gender": "male",
    "weight_kg": 75.0,
    "height_cm": 178.0,
    "goal": "muscle gain",
    "fitness_level": "intermediate",
    "dietary_restrictions": ["no pork"],
    "location": "Kolkata",
}

SEED_WORKOUTS = [
    {
        "workout_type": "strength",
        "duration_min": 60,
        "exercises": [
            {"name": "Bench Press",     "sets": 4, "reps": 8,  "weight_kg": 70},
            {"name": "Squat",           "sets": 4, "reps": 6,  "weight_kg": 90},
            {"name": "Deadlift",        "sets": 3, "reps": 5,  "weight_kg": 110},
            {"name": "Pull-up",         "sets": 3, "reps": 10, "weight_kg": 0},
        ],
        "notes": "Felt strong today. Increased squat weight by 5 kg.",
    },
    {
        "workout_type": "cardio",
        "duration_min": 30,
        "exercises": [],
        "notes": "Morning run on the treadmill.",
    },
]

SEED_MEALS = [
    {
        "meal_type": "breakfast",
        "foods": ["oats", "banana", "boiled eggs (2)", "black coffee"],
        "total_calories": 520,
        "macros": {"protein_g": 28, "carbs_g": 65, "fat_g": 12},
    },
    {
        "meal_type": "lunch",
        "foods": ["grilled chicken breast", "brown rice", "mixed salad"],
        "total_calories": 680,
        "macros": {"protein_g": 52, "carbs_g": 70, "fat_g": 10},
    },
    {
        "meal_type": "dinner",
        "foods": ["paneer curry", "whole wheat roti (2)", "dal"],
        "total_calories": 750,
        "macros": {"protein_g": 38, "carbs_g": 85, "fat_g": 18},
    },
]

SEED_WEIGHTS = [74.2, 74.5, 74.8, 75.0]   # kg, oldest → newest
SEED_CARDIO = [
    {"activity": "running",  "duration_min": 25, "distance_km": 4.0,  "calories": 280},
    {"activity": "cycling",  "duration_min": 40, "distance_km": 14.0, "calories": 320},
]


def seed():
    existing = dump_memory()
    has_data = (
        existing["user_profile"]["name"] is not None
        or existing["workout_history"]
        or existing["meal_logs"]
    )

    if has_data:
        answer = input(
            "memory.json already contains data. Reset and re-seed? [y/N]: "
        ).strip().lower()
        if answer != "y":
            print("Aborted — existing data kept.")
            return

    print("Resetting memory …")
    reset_memory()

    print("Seeding user profile …")
    update_user_profile(**SEED_PROFILE)

    print("Seeding workout history …")
    for w in SEED_WORKOUTS:
        log_workout(**w)

    print("Seeding meal logs …")
    for m in SEED_MEALS:
        log_meal(
            meal_type=m["meal_type"],
            foods=m["foods"],
            total_calories=m["total_calories"],
            macros=m["macros"],
        )

    print("Seeding weight log …")
    for w in SEED_WEIGHTS:
        log_weight(w)

    print("Seeding cardio log …")
    for c in SEED_CARDIO:
        log_cardio(**c)

    print("✅ Seed complete. data/memory.json is ready.")


if __name__ == "__main__":
    seed()
