from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.db import get_db, serialize_doc, to_object_id
from datetime import datetime


habits_bp = Blueprint("habits", __name__)


@habits_bp.get("/ping")
def ping():
    return jsonify(message="habits ok"), 200


@habits_bp.get("/")
@jwt_required()
def list_habits():
    user_id = get_jwt_identity()
    db = get_db()
    docs = [serialize_doc(d) for d in db.habits.find({"user_id": user_id}).sort("created_at", -1)]
    return jsonify(items=docs), 200


@habits_bp.post("/")
@jwt_required()
def create_habit():
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    frequency = (payload.get("frequency") or "").strip()  # daily | weekly | custom
    if not name or not frequency:
        return jsonify(error="Name and frequency are required"), 400
    db = get_db()
    doc = {
        "name": name,
        "frequency": frequency,
        "streak": 0,
        "last_completed_at": None,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    res = db.habits.insert_one(doc)
    created = db.habits.find_one({"_id": res.inserted_id})
    return jsonify(item=serialize_doc(created)), 201


@habits_bp.put("/<habit_id>")
@jwt_required()
def update_habit(habit_id):
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    updates = {}
    for field in ["name", "frequency", "streak"]:
        if field in payload:
            updates[field] = payload[field]
    if "last_completed_at" in payload:
        if payload["last_completed_at"] is None:
            updates["last_completed_at"] = None
        else:
            try:
                updates["last_completed_at"] = datetime.fromisoformat(payload["last_completed_at"])
            except ValueError:
                return jsonify(error="Invalid last_completed_at format"), 400
    if not updates:
        return jsonify(error="No valid fields to update"), 400
    updates["updated_at"] = datetime.utcnow()
    db = get_db()
    res = db.habits.find_one_and_update(
        {"_id": to_object_id(habit_id), "user_id": user_id},
        {"$set": updates},
        return_document=True,
    )
    if not res:
        return jsonify(error="Habit not found"), 404
    return jsonify(item=serialize_doc(res)), 200


@habits_bp.delete("/<habit_id>")
@jwt_required()
def delete_habit(habit_id):
    user_id = get_jwt_identity()
    db = get_db()
    res = db.habits.delete_one({"_id": to_object_id(habit_id), "user_id": user_id})
    if res.deleted_count == 0:
        return jsonify(error="Habit not found"), 404
    return jsonify(status="deleted", id=habit_id), 200


@habits_bp.post("/<habit_id>/complete")
@jwt_required()
def complete_habit(habit_id):
    """Mark habit as completed today and update streak."""
    user_id = get_jwt_identity()
    db = get_db()
    
    habit = db.habits.find_one({"_id": to_object_id(habit_id), "user_id": user_id})
    if not habit:
        return jsonify(error="Habit not found"), 404
    
    now = datetime.utcnow()
    last_completed = habit.get("last_completed_at")
    current_streak = habit.get("streak", 0)
    
    # Check if already completed today
    if last_completed:
        last_date = last_completed.date() if isinstance(last_completed, datetime) else datetime.fromisoformat(str(last_completed)).date()
        if last_date == now.date():
            return jsonify(error="Already completed today", item=serialize_doc(habit)), 200
        
        # Check if streak should continue (completed yesterday)
        days_diff = (now.date() - last_date).days
        if days_diff == 1:
            current_streak += 1
        elif days_diff > 1:
            current_streak = 1  # Reset streak
        else:
            current_streak = 1
    else:
        current_streak = 1
    
    # Update habit
    res = db.habits.find_one_and_update(
        {"_id": to_object_id(habit_id), "user_id": user_id},
        {"$set": {
            "last_completed_at": now,
            "streak": current_streak,
            "updated_at": now,
        }},
        return_document=True,
    )
    
    return jsonify(item=serialize_doc(res), message=f"Streak: {current_streak} days!"), 200
