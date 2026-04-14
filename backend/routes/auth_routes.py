import time
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from firebase_admin import auth as fb_auth
from backend.utils.db import get_db, serialize_doc
from backend.utils.auth_utils import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/ping")
def ping():
    return jsonify(message="auth ok (firebase)"), 200

@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    db = get_db()
    users_ref = db.collection('users')
    existing_user = users_ref.where('email', '==', email).limit(1).get()
    
    if len(existing_user) > 0:
        return jsonify(error="Email already registered"), 409

    # Create user locally in Firestore
    user_data = {
        "email": email,
        "password_hash": hash_password(password),
        "created_at": time.time()
    }
    
    _, doc_ref = users_ref.add(user_data)
    user_snapshot = doc_ref.get()
    doc = serialize_doc(user_snapshot)
    # Remove sensitive info
    doc.pop("password_hash", None)
    
    token = create_access_token(identity=doc["id"])
    return jsonify(user=doc, access_token=token), 201

@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    db = get_db()
    users_ref = db.collection('users')
    query_results = users_ref.where('email', '==', email).limit(1).get()
    
    if len(query_results) == 0:
        return jsonify(error="Invalid credentials"), 401
    
    user_snapshot = query_results[0]
    user_data = user_snapshot.to_dict()
    
    if not verify_password(password, user_data.get("password_hash", "")):
        return jsonify(error="Invalid credentials"), 401

    doc = serialize_doc(user_snapshot)
    doc.pop("password_hash", None)
    token = create_access_token(identity=doc["id"])
    return jsonify(user=doc, access_token=token), 200

@auth_bp.get("/me")
@jwt_required(optional=True)
def me():
    identity = get_jwt_identity()
    if identity is None:
        return jsonify(message="Not authenticated"), 401
    
    db = get_db()
    user_ref = db.collection('users').document(identity)
    user_snapshot = user_ref.get()
    
    if not user_snapshot.exists:
        return jsonify(error="User not found"), 404
    
    doc = serialize_doc(user_snapshot)
    doc.pop("password_hash", None)
    return jsonify(user=doc), 200

@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    db = get_db()
    
    payload = request.get_json(silent=True) or {}
    # Fields allowed to be updated
    allowed_fields = ["name", "username", "goal_minutes", "work_type", "focus_method"]
    updates = {k: v for k, v in payload.items() if k in allowed_fields}
    
    if not updates:
        return jsonify(error="No valid update fields provided"), 400
        
    user_ref = db.collection('users').document(identity)
    user_ref.update(updates)
    
    updated_snapshot = user_ref.get()
    doc = serialize_doc(updated_snapshot)
    doc.pop("password_hash", None)
    
    return jsonify(message="Profile updated successfully", user=doc), 200

@auth_bp.post("/firebase")
def firebase_auth_endpoint():
    """
    Verifies a Firebase ID token and returns a local JWT.
    Handles 'Token used too early' by retrying once.
    """
    db = get_db() # Initializes Firebase if needed
    
    payload = request.get_json(silent=True) or {}
    id_token = payload.get("idToken")
    
    if not id_token:
        return jsonify(error="ID token is required"), 400
        
    decoded_token = None
    try:
        # Attempt verification
        decoded_token = fb_auth.verify_id_token(id_token)
    except Exception as e:
        err_msg = str(e)
        # Handle clock skew: "Token used too early"
        if "too early" in err_msg.lower():
            print("DEBUG: Firebase token used too early (clock drift). Retrying in 2 seconds...")
            time.sleep(2)
            try:
                decoded_token = fb_auth.verify_id_token(id_token)
            except Exception as e2:
                print(f"ERROR: Firebase Auth Error after retry: {e2}")
                return jsonify(error=f"Token validation failed: {str(e2)}"), 401
        else:
            print(f"ERROR: Firebase Auth Error: {err_msg}")
            return jsonify(error="Invalid Firebase token"), 401
    
    if not decoded_token:
        return jsonify(error="Failed to decode token"), 401

    uid = decoded_token['uid']
    email = decoded_token.get('email')
    name = decoded_token.get('name', '')
    picture = decoded_token.get('picture', '')
    
    users_ref = db.collection('users')
    user_doc_ref = users_ref.document(uid)
    user_snapshot = user_doc_ref.get()
    
    if not user_snapshot.exists:
        user_data = {
            "email": email,
            "name": name,
            "picture": picture,
            "firebase_uid": uid,
            "created_at": time.time()
        }
        user_doc_ref.set(user_data)
        print(f"DEBUG: Created new user from Firebase: {email}")
    else:
        # Update existing user info
        user_doc_ref.update({
            "name": name,
            "picture": picture,
            "last_login": time.time()
        })
        print(f"DEBUG: Logged in existing Firebase user: {email}")
        
    doc = serialize_doc(user_doc_ref.get())
    token = create_access_token(identity=uid)
    return jsonify(user=doc, access_token=token), 200
