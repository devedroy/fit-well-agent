"""
Tools available to the FitWell agent.

Each function is decorated with @tool so LangChain/LangGraph can
discover it and Gemini can call it via function-calling.

All persistence goes through database.db_manager (memory.json).
"""

import json
import os
from langchain_core.tools import tool
from database.db_manager import (
    get_user_profile,
    update_user_profile,
    log_workout,
    get_workout_history,
    log_meal,
    get_meal_logs,
    log_weight,
    log_strength,
    log_cardio,
    get_progress_tracking,
)


# ──────────────────────────────────────────────
# Profile Tools
# ──────────────────────────────────────────────

@tool
def fetch_user_profile() -> str:
    """
    Retrieve the user's stored profile including name, age, weight,
    height, goal, fitness level, dietary restrictions, and location.
    Call this first to personalise any recommendation.
    """
    profile = get_user_profile()
    return json.dumps(profile, indent=2)


@tool
def save_user_profile(
    name: str = None,
    age: int = None,
    gender: str = None,
    weight_kg: float = None,
    height_cm: float = None,
    goal: str = None,
    fitness_level: str = None,
    dietary_restrictions: list = None,
    location: str = None,
) -> str:
    """
    Update one or more fields of the user profile and persist to memory.
    Only pass the fields you want to change; omit the rest.

    Args:
        name:                  Full name.
        age:                   Age in years.
        gender:                'male' | 'female' | 'other'
        weight_kg:             Body weight in kilograms.
        height_cm:             Height in centimetres.
        goal:                  Primary fitness goal, e.g. 'weight loss',
                               'muscle gain', 'endurance'.
        fitness_level:         'beginner' | 'intermediate' | 'advanced'
        dietary_restrictions:  List of restrictions, e.g. ['vegan', 'gluten-free']
        location:              City / neighbourhood for gym search.
    """
    kwargs = {k: v for k, v in {
        "name": name, "age": age, "gender": gender,
        "weight_kg": weight_kg, "height_cm": height_cm,
        "goal": goal, "fitness_level": fitness_level,
        "dietary_restrictions": dietary_restrictions,
        "location": location,
    }.items() if v is not None}
    updated = update_user_profile(**kwargs)
    return f"Profile updated: {json.dumps(updated, indent=2)}"


# ──────────────────────────────────────────────
# Workout Tools
# ──────────────────────────────────────────────

@tool
def record_workout(
    workout_type: str,
    duration_min: int,
    exercises: list,
    notes: str = "",
) -> str:
    """
    Log a completed workout session.

    Args:
        workout_type:  Category, e.g. 'strength', 'cardio', 'yoga', 'hiit'.
        duration_min:  Total session length in minutes.
        exercises:     List of exercise dicts, each with keys:
                       name (str), sets (int), reps (int), weight_kg (float).
        notes:         Any extra observations (optional).
    """
    entry = log_workout(workout_type, duration_min, exercises, notes)
    return f"Workout logged (id={entry['id']}): {json.dumps(entry, indent=2)}"


@tool
def get_recent_workouts(limit: int = 10) -> str:
    """
    Retrieve the most recent workout sessions.

    Args:
        limit: How many sessions to return (default 10, max 20).
    """
    history = get_workout_history(min(limit, 20))
    return json.dumps(history, indent=2)


# ──────────────────────────────────────────────
# Meal Tools
# ──────────────────────────────────────────────

@tool
def record_meal(
    meal_type: str,
    foods: list,
    total_calories: int,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
) -> str:
    """
    Log a meal with its macronutrient breakdown.

    Args:
        meal_type:       'breakfast' | 'lunch' | 'dinner' | 'snack'
        foods:           List of food item strings.
        total_calories:  Estimated calories for the full meal.
        protein_g:       Grams of protein.
        carbs_g:         Grams of carbohydrates.
        fat_g:           Grams of fat.
    """
    macros = {"protein_g": protein_g, "carbs_g": carbs_g, "fat_g": fat_g}
    entry = log_meal(meal_type, foods, total_calories, macros)
    return f"Meal logged (id={entry['id']}): {json.dumps(entry, indent=2)}"


@tool
def get_recent_meals(limit: int = 14) -> str:
    """
    Retrieve the most recent meal log entries.

    Args:
        limit: Number of entries to return (default 14, max 30).
    """
    meals = get_meal_logs(min(limit, 30))
    return json.dumps(meals, indent=2)


# ──────────────────────────────────────────────
# Progress Tools
# ──────────────────────────────────────────────

@tool
def record_weight(weight_kg: float) -> str:
    """
    Log today's body weight.

    Args:
        weight_kg: Current body weight in kilograms.
    """
    entry = log_weight(weight_kg)
    return f"Weight logged: {json.dumps(entry)}"


@tool
def record_strength_pr(
    exercise: str,
    weight_kg: float,
    reps: int,
    sets: int,
) -> str:
    """
    Log a strength / personal record entry.

    Args:
        exercise:  Exercise name, e.g. 'bench press'.
        weight_kg: Weight lifted in kg.
        reps:      Repetitions performed.
        sets:      Number of sets.
    """
    entry = log_strength(exercise, weight_kg, reps, sets)
    return f"Strength PR logged: {json.dumps(entry)}"


@tool
def record_cardio(
    activity: str,
    duration_min: int,
    distance_km: float = None,
    calories: int = None,
) -> str:
    """
    Log a cardio session.

    Args:
        activity:     Type of cardio, e.g. 'running', 'cycling', 'swimming'.
        duration_min: Duration in minutes.
        distance_km:  Distance covered in km (optional).
        calories:     Calories burned (optional).
    """
    entry = log_cardio(activity, duration_min, distance_km, calories)
    return f"Cardio logged: {json.dumps(entry)}"


@tool
def get_progress_summary() -> str:
    """
    Return the full progress tracking data — weight log, strength log,
    and cardio log — so the agent can summarise trends.
    """
    progress = get_progress_tracking()
    return json.dumps(progress, indent=2)


# ──────────────────────────────────────────────
# Location / Facility Search (Dummy Data)
# No external API key required.  Set USE_DUMMY_MAP_DATA=true in .env.
# ──────────────────────────────────────────────

DUMMY_FACILITIES = [
    # ── Gyms / Fitness Centres ─────────────────
    {"name": "IronHouse Gym",           "type": "gym",    "address": "12 Oak Street, Downtown",        "rating": 4.6, "distance_km": 0.8,  "hours": "05:00–23:00", "amenities": ["weights", "cardio machines", "sauna"]},
    {"name": "FitZone Fitness Centre",  "type": "gym",    "address": "45 Park Avenue, Midtown",        "rating": 4.4, "distance_km": 1.2,  "hours": "06:00–22:00", "amenities": ["weights", "group classes", "pool"]},
    {"name": "Apex Strength Club",      "type": "gym",    "address": "88 Maple Road, Uptown",          "rating": 4.8, "distance_km": 1.5,  "hours": "05:30–22:30", "amenities": ["powerlifting", "olympic lifting", "coaching"]},
    {"name": "Planet Power Gym",        "type": "gym",    "address": "3 Commerce Blvd, East Side",     "rating": 4.1, "distance_km": 2.0,  "hours": "24/7",        "amenities": ["cardio machines", "weights", "tanning"]},
    {"name": "Velocity Athletic Club",  "type": "gym",    "address": "71 Harbor View, West End",       "rating": 4.7, "distance_km": 2.4,  "hours": "06:00–21:00", "amenities": ["weights", "hiit studio", "recovery room"]},
    {"name": "CoreFlex Gym",            "type": "gym",    "address": "22 Union Lane, South Quarter",   "rating": 4.3, "distance_km": 3.1,  "hours": "06:00–22:00", "amenities": ["functional training", "weights", "foam rolling"]},

    # ── Yoga & Pilates Studios ─────────────────
    {"name": "Serenity Yoga Studio",    "type": "yoga",   "address": "9 Blossom Court, Old Town",      "rating": 4.9, "distance_km": 0.5,  "hours": "07:00–20:00", "amenities": ["hot yoga", "meditation", "props provided"]},
    {"name": "Balance Pilates",         "type": "yoga",   "address": "33 Crescent Drive, Midtown",     "rating": 4.7, "distance_km": 1.0,  "hours": "06:30–19:30", "amenities": ["reformer pilates", "mat classes", "prenatal"]},
    {"name": "ZenFlow Studio",          "type": "yoga",   "address": "55 Lily Lane, North District",   "rating": 4.6, "distance_km": 1.8,  "hours": "07:00–21:00", "amenities": ["vinyasa", "yin yoga", "breathwork"]},
    {"name": "Inner Light Yoga",        "type": "yoga",   "address": "104 Fern Alley, West End",       "rating": 4.5, "distance_km": 2.7,  "hours": "08:00–20:00", "amenities": ["ashtanga", "restorative yoga", "workshop space"]},

    # ── Outdoor Parks & Tracks ─────────────────
    {"name": "Riverside Park Trail",    "type": "park",   "address": "Riverside Promenade, Riverbank", "rating": 4.8, "distance_km": 0.3,  "hours": "Always open", "amenities": ["5 km loop", "outdoor gym", "water stations"]},
    {"name": "Central Memorial Park",   "type": "park",   "address": "Central Park Road, Downtown",    "rating": 4.7, "distance_km": 0.9,  "hours": "Always open", "amenities": ["jogging track", "pull-up bars", "benches"]},
    {"name": "Highland Sports Ground",  "type": "park",   "address": "15 Highland Ave, North District","rating": 4.5, "distance_km": 2.1,  "hours": "06:00–21:00", "amenities": ["athletics track", "football pitch", "outdoor gym"]},
    {"name": "Lakeside Nature Reserve", "type": "park",   "address": "Lake Road, South Quarter",       "rating": 4.9, "distance_km": 3.5,  "hours": "Always open", "amenities": ["trail running", "lake swimming area", "picnic zone"]},

    # ── CrossFit Boxes ─────────────────────────
    {"name": "CrossFit Catalyst",       "type": "crossfit","address": "77 Industrial Way, East Side",  "rating": 4.8, "distance_km": 1.7,  "hours": "05:30–21:00", "amenities": ["open gym", "coached WODs", "mobility classes"]},
    {"name": "FireBreath CrossFit",     "type": "crossfit","address": "28 Steel Street, South Quarter","rating": 4.6, "distance_km": 2.9,  "hours": "06:00–20:30", "amenities": ["barbell coaching", "endurance track", "nutrition guidance"]},

    # ── Swimming Pools ─────────────────────────
    {"name": "Aqua Fit Centre",         "type": "pool",   "address": "6 Waterside Close, West End",    "rating": 4.4, "distance_km": 1.3,  "hours": "06:00–21:00", "amenities": ["25 m lanes", "aqua aerobics", "kids pool"]},
    {"name": "Olympic Aquatics Complex","type": "pool",   "address": "Stadium Drive, North District",  "rating": 4.7, "distance_km": 2.6,  "hours": "05:30–22:00", "amenities": ["50 m pool", "diving boards", "sauna"]},

    # ── Cycling Studios ─────────────────────────
    {"name": "Spin Republic",           "type": "cycling","address": "40 Gear Road, Midtown",          "rating": 4.5, "distance_km": 0.7,  "hours": "06:00–21:00", "amenities": ["spin bikes", "power meters", "shower rooms"]},
    {"name": "CycleZone Studio",        "type": "cycling","address": "19 Spoke Lane, East Side",       "rating": 4.3, "distance_km": 1.6,  "hours": "07:00–20:00", "amenities": ["group rides", "beginner classes", "bike fitting"]},
]


@tool
def find_nearby_facilities(
    facility_type: str = "all",
    keyword: str = "",
    max_results: int = 5,
    max_distance_km: float = 10.0,
) -> str:
    """
    Search for nearby fitness facilities using built-in dummy data.

    Args:
        facility_type: Filter by category — 'gym', 'yoga', 'park', 'crossfit',
                       'pool', 'cycling', or 'all' (default).
        keyword:       Optional text to match against facility name or amenities.
        max_results:   Maximum number of results to return (default 5, max 10).
        max_distance_km: Only include facilities within this distance (default 10 km).
    """
    results = DUMMY_FACILITIES

    # Filter by type
    if facility_type and facility_type.lower() != "all":
        results = [f for f in results if f["type"] == facility_type.lower()]

    # Filter by distance
    results = [f for f in results if f["distance_km"] <= max_distance_km]

    # Filter by keyword (name or amenities)
    if keyword:
        kw = keyword.lower()
        results = [
            f for f in results
            if kw in f["name"].lower() or any(kw in a.lower() for a in f["amenities"])
        ]

    # Sort by distance, cap results
    results = sorted(results, key=lambda f: f["distance_km"])[: min(max_results, 10)]

    if not results:
        return json.dumps({"message": "No facilities found matching your criteria.", "results": []})

    return json.dumps({"count": len(results), "results": results}, indent=2)


# ──────────────────────────────────────────────
# All tools exported for agent binding
# ──────────────────────────────────────────────

ALL_TOOLS = [
    fetch_user_profile,
    save_user_profile,
    record_workout,
    get_recent_workouts,
    record_meal,
    get_recent_meals,
    record_weight,
    record_strength_pr,
    record_cardio,
    get_progress_summary,
    find_nearby_facilities,
]
