from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.db import get_db, serialize_doc
from datetime import datetime
from google.cloud import firestore


habits_bp = Blueprint("habits", __name__)


@habits_bp.get("/ping")
def ping():
    return jsonify(message="habits ok (firebase)"), 200


@habits_bp.get("/")
@jwt_required()
def list_habits():
    user_id = get_jwt_identity()
    db = get_db()
    
    habits_ref = db.collection('habits')
    query = habits_ref.where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
    
    try:
        docs = [serialize_doc(d) for d in query.get()]
    except Exception:
        raw_docs = habits_ref.where('user_id', '==', user_id).get()
        data = [serialize_doc(d) for d in raw_docs]
        data.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        docs = data
        
    return jsonify(items=docs), 200


@habits_bp.post("/")
@jwt_required()
def create_habit():
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    frequency = (payload.get("frequency") or "").strip()
    if not name or not frequency:
        return jsonify(error="Name and frequency are required"), 400
        
    db = get_db()
    doc_data = {
        "name": name,
        "frequency": frequency,
        "streak": 0,
        "last_completed_at": None,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    doc_ref = db.collection('habits').add(doc_data)[1]
    created_snapshot = doc_ref.get()
    
    return jsonify(item=serialize_doc(created_snapshot)), 201


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
    habit_ref = db.collection('habits').document(habit_id)
    habit_snapshot = habit_ref.get()
    
    if not habit_snapshot.exists or habit_snapshot.to_dict().get('user_id') != user_id:
        return jsonify(error="Habit not found"), 404
        
    habit_ref.update(updates)
    updated_snapshot = habit_ref.get()
    
    return jsonify(item=serialize_doc(updated_snapshot)), 200


@habits_bp.delete("/<habit_id>")
@jwt_required()
def delete_habit(habit_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    habit_ref = db.collection('habits').document(habit_id)
    habit_snapshot = habit_ref.get()
    
    if not habit_snapshot.exists or habit_snapshot.to_dict().get('user_id') != user_id:
        return jsonify(error="Habit not found"), 404
        
    habit_ref.delete()
    return jsonify(status="deleted", id=habit_id), 200


@habits_bp.post("/<habit_id>/complete")
@jwt_required()
def complete_habit(habit_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    habit_ref = db.collection('habits').document(habit_id)
    habit_snapshot = habit_ref.get()
    
    if not habit_snapshot.exists or habit_snapshot.to_dict().get('user_id') != user_id:
        return jsonify(error="Habit not found"), 404
        
    habit = habit_snapshot.to_dict()
    now = datetime.utcnow()
    last_completed = habit.get("last_completed_at")
    current_streak = habit.get("streak", 0)
    
    if last_completed:
        last_date = last_completed.date() if isinstance(last_completed, datetime) else datetime.fromisoformat(str(last_completed)).date()
        if last_date == now.date():
            return jsonify(error="Already completed today", item=serialize_doc(habit_snapshot)), 200
        
        days_diff = (now.date() - last_date).days
        if days_diff == 1:
            current_streak += 1
        elif days_diff > 1:
            current_streak = 1
        else:
            current_streak = 1
    else:
        current_streak = 1
    
    updates = {
        "last_completed_at": now,
        "streak": current_streak,
        "updated_at": now,
    }
    
    habit_ref.update(updates)
    updated_snapshot = habit_ref.get()
    
    return jsonify(item=serialize_doc(updated_snapshot), message=f"Streak: {current_streak} days!"), 200
