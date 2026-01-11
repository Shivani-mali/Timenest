from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from backend.utils.db import get_db, serialize_doc, to_object_id
from backend.utils.auth_utils import hash_password, verify_password
from pymongo.errors import DuplicateKeyError


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/ping")
def ping():
    return jsonify(message="auth ok"), 200


@auth_bp.post("/register")
def register():
    from backend.utils.db import ensure_indexes
    ensure_indexes()  # Lazy index creation on first auth operation
    
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    db = get_db()
    try:
        res = db.users.insert_one({
            "email": email,
            "password_hash": hash_password(password),
        })
    except DuplicateKeyError:
        return jsonify(error="Email already registered"), 409

    user = db.users.find_one({"_id": res.inserted_id})
    doc = serialize_doc(user)
    token = create_access_token(identity=doc["id"])
    return jsonify(user={"id": doc["id"], "email": doc["email"]}, access_token=token), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    db = get_db()
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        return jsonify(error="Invalid credentials"), 401

    doc = serialize_doc(user)
    token = create_access_token(identity=doc["id"])
    return jsonify(user={"id": doc["id"], "email": doc["email"]}, access_token=token), 200


@auth_bp.get("/me")
@jwt_required(optional=True)
def me():
    identity = get_jwt_identity()
    if identity is None:
        return jsonify(message="Not authenticated"), 401
    db = get_db()
    user = db.users.find_one({"_id": to_object_id(identity)})
    if not user:
        return jsonify(error="User not found"), 404
    doc = serialize_doc(user)
    return jsonify(user={"id": doc["id"], "email": doc["email"]}), 200
