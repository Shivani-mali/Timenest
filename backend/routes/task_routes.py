from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.db import get_db, serialize_doc
from datetime import datetime
from google.cloud import firestore


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/ping")
def ping():
    return jsonify(message="tasks ok (firebase)"), 200


@tasks_bp.get("/")
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()
    db = get_db()
    
    # Simple query first. Note: Composite index may be required for complex ordering.
    tasks_ref = db.collection('tasks')
    query = tasks_ref.where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
    
    try:
        docs = [serialize_doc(d) for d in query.get()]
    except Exception:
        # Fallback if index isn't created yet: get matching docs and sort in memory
        raw_docs = tasks_ref.where('user_id', '==', user_id).get()
        data = [serialize_doc(d) for d in raw_docs]
        data.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        docs = data
        
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
    priority = payload.get("priority")
    due_date = payload.get("due_date")
    due_time = payload.get("due_time")

    due_dt = None
    if due_date:
        if due_time:
            try:
                due_dt = datetime.fromisoformat(f"{due_date}T{due_time}")
            except ValueError:
                return jsonify(error="Invalid due_date or due_time format"), 400
        else:
            try:
                due_dt = datetime.fromisoformat(due_date)
            except ValueError:
                return jsonify(error="Invalid due_date format"), 400

    db = get_db()
    doc_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_dt,
        "due_time": due_time,
        "completed": False,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    doc_ref = db.collection('tasks').add(doc_data)[1]
    created_snapshot = doc_ref.get()
    
    return jsonify(item=serialize_doc(created_snapshot)), 201


@tasks_bp.put("/<task_id>")
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    updates = {}
    for field in ["title", "description", "priority", "completed"]:
        if field in payload:
            updates[field] = payload[field]
            
    if "due_date" in payload or "due_time" in payload:
        raw_date = payload.get("due_date")
        raw_time = payload.get("due_time")

        if raw_date is None and raw_time is None:
            updates["due_date"] = None
            updates["due_time"] = None
        elif raw_date is not None and raw_time:
            try:
                updates["due_date"] = datetime.fromisoformat(f"{raw_date}T{raw_time}")
            except ValueError:
                return jsonify(error="Invalid due_date or due_time format"), 400
            updates["due_time"] = raw_time
        elif raw_date is not None and (raw_time is None or raw_time == ""):
            try:
                updates["due_date"] = datetime.fromisoformat(str(raw_date))
            except ValueError:
                return jsonify(error="Invalid due_date format"), 400
            updates["due_time"] = None
        elif raw_date is None and raw_time:
            updates["due_time"] = raw_time
            
    if not updates:
        return jsonify(error="No valid fields to update"), 400
        
    updates["updated_at"] = datetime.utcnow()

    db = get_db()
    task_ref = db.collection('tasks').document(task_id)
    task_snapshot = task_ref.get()
    
    if not task_snapshot.exists or task_snapshot.to_dict().get('user_id') != user_id:
        return jsonify(error="Task not found"), 404
        
    task_ref.update(updates)
    updated_snapshot = task_ref.get()
    
    return jsonify(item=serialize_doc(updated_snapshot)), 200


@tasks_bp.delete("/<task_id>")
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    task_ref = db.collection('tasks').document(task_id)
    task_snapshot = task_ref.get()
    
    if not task_snapshot.exists or task_snapshot.to_dict().get('user_id') != user_id:
        return jsonify(error="Task not found"), 404
        
    task_ref.delete()
    return jsonify(status="deleted", id=task_id), 200
