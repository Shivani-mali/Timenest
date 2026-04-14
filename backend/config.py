import os
from datetime import timedelta

class Config:
    """Flask configuration for TimeNest Backend."""
    
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "prod-secret-key-required")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-prod-secret-key-required")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("JWT_EXPIRES_HOURS", "24")))

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_KEY = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY", "backend/serviceAccountKey.json")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")

    # App Settings
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    JSON_SORT_KEYS = False
    
    # For backward compatibility / future use
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "127.0.0.1")
