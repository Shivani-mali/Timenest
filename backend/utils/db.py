from pymongo import MongoClient, ASCENDING
from flask import current_app
from bson import ObjectId
from datetime import datetime

_client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = current_app.config["MONGO_URI"]
        _client = MongoClient(uri, connect=False)
    return _client


def get_db():
    db_name = current_app.config["MONGO_DB_NAME"]
    return get_client()[db_name]


def close_db(_=None):
    global _client
    if _client is not None:
        _client.close()
        _client = None


def init_app(app):
    app.teardown_appcontext(close_db)


def ensure_indexes():
    """Create indexes on first use (lazy initialization)."""
    db = get_db()
    try:
        db.users.create_index([("email", ASCENDING)], unique=True, name="uq_user_email")
    except Exception:
        pass  # Index may already exist


def to_object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)


def serialize_id(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value


def serialize_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    out = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = serialize_id(v)
        else:
            out[k] = serialize_datetime(v)
    return out
