from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.db import get_db, serialize_doc, to_object_id
from datetime import datetime


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/ping")
def ping():
    return jsonify(message="tasks ok"), 200


@tasks_bp.get("/")
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()
    db = get_db()
    docs = [serialize_doc(d) for d in db.tasks.find({"user_id": user_id}).sort("created_at", -1)]
    return jsonify(items=docs), 200


@tasks_bp.post("/")
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify(error="Title is required"), 400
    description = payload.get("description")
    priority = payload.get("priority")  # low | medium | high
    due_date = payload.get("due_date")  # ISO string
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date)
        except ValueError:
            return jsonify(error="Invalid due_date format"), 400
    else:
        due_dt = None

    db = get_db()
    doc = {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_dt,
        "completed": False,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    res = db.tasks.insert_one(doc)
    created = db.tasks.find_one({"_id": res.inserted_id})
    return jsonify(item=serialize_doc(created)), 201


@tasks_bp.put("/<task_id>")
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    updates = {}
    for field in ["title", "description", "priority", "completed"]:
        if field in payload:
            updates[field] = payload[field]
    if "due_date" in payload:
        if payload["due_date"] is None:
            updates["due_date"] = None
        else:
            try:
                updates["due_date"] = datetime.fromisoformat(payload["due_date"])
            except ValueError:
                return jsonify(error="Invalid due_date format"), 400
    if not updates:
        return jsonify(error="No valid fields to update"), 400
    updates["updated_at"] = datetime.utcnow()

    db = get_db()
    res = db.tasks.find_one_and_update(
        {"_id": to_object_id(task_id), "user_id": user_id},
        {"$set": updates},
        return_document=True,
    )
    if not res:
        return jsonify(error="Task not found"), 404
    return jsonify(item=serialize_doc(res)), 200


@tasks_bp.delete("/<task_id>")
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    db = get_db()
    res = db.tasks.delete_one({"_id": to_object_id(task_id), "user_id": user_id})
    if res.deleted_count == 0:
        return jsonify(error="Task not found"), 404
    return jsonify(status="deleted", id=task_id), 200
