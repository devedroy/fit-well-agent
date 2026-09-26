"""
Tools available to the FitWell agent.

Each function is decorated with @tool so LangChain/LangGraph can
discover it and Gemini can call it via function-calling.

All persistence goes through database.db_manager (memory.json).
"""

import json
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
]
