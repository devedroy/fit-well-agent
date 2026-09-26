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
    get_workout_history,
    get_meal_logs,
    get_progress_tracking,
    reset_memory,
    _load,
)
from graph.agent import chat as agent_chat

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
def dump_memory():
    """Return the full memory.json document (useful for debugging)."""
    return jsonify(_load())


@bp.route("/api/memory/reset", methods=["POST"])
def do_reset_memory():
    """Wipe all memory data and restart fresh."""
    reset_memory()
    return jsonify({"status": "reset complete"})


# ── Progress & History ─────────────────────────────────────────────────────────

@bp.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(get_progress_tracking())


@bp.route("/api/workouts", methods=["GET"])
def get_workouts():
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_workout_history(limit))


@bp.route("/api/meals", methods=["GET"])
def get_meals():
    limit = request.args.get("limit", 14, type=int)
    return jsonify(get_meal_logs(limit))


@bp.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(get_conversation_history())
