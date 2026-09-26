"""
Flask REST routes for the FitWell agent.

Endpoints:
  GET  /                      → Serve the dashboard SPA
  POST /api/chat              → Chat with the agent
  GET  /api/profile           → Read user profile
  POST /api/profile           → Update user profile
  GET  /api/memory            → Dump full memory.json (debug)
  POST /api/memory/reset      → Reset memory to blank state
  GET  /api/progress          → Fetch progress tracking data
  GET  /api/workouts          → Fetch recent workouts
  GET  /api/meals             → Fetch recent meals
"""

from flask import Blueprint, jsonify, request, render_template
from database.db_manager import (
    get_user_profile,
    update_user_profile,
    get_conversation_history,
    clear_conversation_history,
    get_workout_history,
    log_workout,
    get_meal_logs,
    log_meal,
    get_progress_tracking,
    log_weight,
    log_strength,
    reset_memory,
    dump_memory,
)
from graph.agent import chat as agent_chat
from graph.tools import DUMMY_FACILITIES
from database.seed_data import seed as run_seed

bp = Blueprint("main", __name__)



# ── Dashboard ──────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    return render_template("index.html")


# ── Chat ───────────────────────────────────────────────────────────────────────

@bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Body: { "message": "..." }
    Returns: { "response": "..." }
    """
    body = request.get_json(silent=True) or {}
    user_message = body.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    try:
        response = agent_chat(user_message)
        return jsonify({"response": response})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Profile ────────────────────────────────────────────────────────────────────

@bp.route("/api/profile", methods=["GET"])
def get_profile():
    return jsonify(get_user_profile())


@bp.route("/api/profile", methods=["POST"])
def post_profile():
    """
    Body: any subset of profile fields.
    Returns: updated profile.
    """
    body = request.get_json(silent=True) or {}
    allowed_keys = {
        "name", "age", "gender", "weight_kg", "height_cm",
        "goal", "fitness_level", "dietary_restrictions", "location",
    }
    kwargs = {k: v for k, v in body.items() if k in allowed_keys}
    if not kwargs:
        return jsonify({"error": "No valid fields provided"}), 400
    updated = update_user_profile(**kwargs)
    return jsonify(updated)


# ── Memory Debug ───────────────────────────────────────────────────────────────

@bp.route("/api/memory", methods=["GET"])
def get_memory_dump():
    """Return the full memory.json document (useful for debugging)."""
    return jsonify(dump_memory())


@bp.route("/api/memory/reset", methods=["POST"])
def do_reset_memory():
    """Wipe all memory data and restart fresh."""
    reset_memory()
    return jsonify({"status": "reset complete"})


@bp.route("/api/memory/seed", methods=["POST"])
def do_seed_memory():
    """Re-seed memory with demo starter data."""
    run_seed(force=True)
    return jsonify({"status": "seed complete"})


# ── Progress & History ─────────────────────────────────────────────────────────

@bp.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(get_progress_tracking())


@bp.route("/api/progress/weight", methods=["POST"])
def post_weight():
    """Body: { "weight_kg": 75.2 }"""
    body = request.get_json(silent=True) or {}
    weight = body.get("weight_kg")
    if weight is None:
        return jsonify({"error": "weight_kg is required"}), 400
    try:
        entry = log_weight(float(weight))
        # Also update user_profile current weight
        update_user_profile(weight_kg=float(weight))
        return jsonify(entry)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid weight value: {exc}"}), 400


@bp.route("/api/workouts", methods=["GET"])
def get_workouts():
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_workout_history(limit))


@bp.route("/api/workouts", methods=["POST"])
def post_workout():
    """
    Body: {
        "workout_type": "strength",
        "duration_min": 45,
        "exercises": [...],
        "notes": "..."
    }
    """
    body = request.get_json(silent=True) or {}
    workout_type = body.get("workout_type", "workout").strip()
    duration_min = int(body.get("duration_min", 30))
    exercises = body.get("exercises", [])
    notes = body.get("notes", "")

    entry = log_workout(
        workout_type=workout_type,
        duration_min=duration_min,
        exercises=exercises,
        notes=notes,
    )
    return jsonify(entry), 201


@bp.route("/api/meals", methods=["GET"])
def get_meals():
    limit = request.args.get("limit", 14, type=int)
    return jsonify(get_meal_logs(limit))


@bp.route("/api/meals", methods=["POST"])
def post_meal():
    """
    Body: {
        "meal_type": "lunch",
        "foods": ["chicken", "rice"],
        "total_calories": 550,
        "macros": {"protein_g": 40, "carbs_g": 60, "fat_g": 10}
    }
    """
    body = request.get_json(silent=True) or {}
    meal_type = body.get("meal_type", "snack")
    foods = body.get("foods", [])
    if isinstance(foods, str):
        foods = [f.strip() for f in foods.split(",") if f.strip()]
    total_calories = int(body.get("total_calories", 0))
    macros = body.get("macros", {
        "protein_g": float(body.get("protein_g", 0)),
        "carbs_g": float(body.get("carbs_g", 0)),
        "fat_g": float(body.get("fat_g", 0)),
    })

    entry = log_meal(
        meal_type=meal_type,
        foods=foods,
        total_calories=total_calories,
        macros=macros,
    )
    return jsonify(entry), 201


@bp.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(get_conversation_history())


@bp.route("/api/history/clear", methods=["POST"])
def do_clear_history():
    clear_conversation_history()
    return jsonify({"status": "history cleared"})


# ── Facilities (Map / Location) ────────────────────────────────────────────────

@bp.route("/api/facilities", methods=["GET"])
def get_facilities():
    facility_type = request.args.get("type", "all").strip().lower()
    keyword = request.args.get("keyword", "").strip().lower()
    max_distance = request.args.get("max_distance", 15.0, type=float)
    limit = request.args.get("limit", 20, type=int)

    results = list(DUMMY_FACILITIES)

    if facility_type and facility_type != "all":
        results = [f for f in results if f["type"].lower() == facility_type]

    results = [f for f in results if f["distance_km"] <= max_distance]

    if keyword:
        results = [
            f for f in results
            if keyword in f["name"].lower() or any(keyword in a.lower() for a in f.get("amenities", []))
        ]

    results = sorted(results, key=lambda f: f["distance_km"])[:limit]
    return jsonify({"count": len(results), "facilities": results})

