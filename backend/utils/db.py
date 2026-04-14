import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import current_app
from datetime import datetime

_db = None

def get_db(app=None):
    """
    Returns the Firestore client, initializing Firebase if necessary.
    """
    global _db
    if _db is None:
        if not firebase_admin._apps:
            # 1. Try to get credentials from environment variable (JSON string)
            firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
            cred = None
            
            if firebase_json:
                try:
                    import json
                    service_account_info = json.loads(firebase_json)
                    cred = credentials.Certificate(service_account_info)
                    print("DEBUG: Initializing Firebase using FIREBASE_SERVICE_ACCOUNT_JSON env var.")
                except Exception as e:
                    print(f"ERROR: Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

            # 2. Fallback to file-based credentials
            if not cred:
                app_config = app.config if app else current_app.config
                key_path = app_config.get("FIREBASE_SERVICE_ACCOUNT_KEY")
                
                if key_path and not os.path.isabs(key_path):
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    possible_paths = [
                        os.path.abspath(key_path),
                        os.path.join(project_root, key_path),
                        os.path.join(os.getcwd(), key_path),
                        os.path.join(os.path.dirname(os.path.dirname(__file__)), "serviceAccountKey.json")
                    ]
                    
                    for p in possible_paths:
                        if os.path.exists(p):
                            key_path = p
                            break
                
                if key_path and os.path.exists(key_path):
                    print(f"DEBUG: Initializing Firebase with key file: {key_path}")
                    cred = credentials.Certificate(key_path)
                else:
                    if not firebase_json:
                        raise FileNotFoundError("Firebase credentials not found (tried env var and file).")

            if cred:
                try:
                    firebase_admin.initialize_app(cred)
                    print("DEBUG: Firebase Admin SDK initialized successfully.")
                except Exception as e:
                    print(f"ERROR: Failed to initialize Firebase Admin SDK: {e}")
                    raise
        
        _db = firestore.client()
    return _db

def serialize_doc(doc_snapshot) -> dict:
    """Converts Firestore snapshot to a JSON-serializable dict."""
    if not doc_snapshot or not hasattr(doc_snapshot, 'exists') or not doc_snapshot.exists:
        return None
    
    data = doc_snapshot.to_dict()
    data['id'] = doc_snapshot.id
    
    # Convert datetimes to ISO strings
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = v.isoformat()
    return data
