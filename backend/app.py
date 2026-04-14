import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables from backend/.env
# We look for .env in the same directory as this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def create_app():
    # Point Flask to the frontend folder (one level up from backend/)
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
    
    app = Flask(__name__, 
                static_folder=FRONTEND_DIR,
                static_url_path="",
                template_folder=FRONTEND_DIR)
    
    # Load configuration from backend/config.py
    app.config.from_object("backend.config.Config")
    
    # Core extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    JWTManager(app)

    # Initialize Firebase/Firestore early to catch errors
    from backend.utils.db import get_db
    try:
        get_db(app)
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase during startup: {e}")

    # Register blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.task_routes import tasks_bp
    from backend.routes.habit_routes import habits_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")

    # Serve the frontend index.html at root
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")
    
    # Serve other static files/pages with fallback to .html
    @app.route("/<path:path>")
    def serve_frontend(path):
        # 1. Try exact file (e.g. css/style.css)
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # 2. Try adding .html (e.g. /login -> login.html)
        if os.path.exists(os.path.join(app.static_folder, f"{path}.html")):
            return send_from_directory(app.static_folder, f"{path}.html")
        # 3. Fallback to 404
        return jsonify(error="Not Found", path=path), 404

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="TimeNest API", environment=os.environ.get("FLASK_ENV", "dev")), 200

    return app

# Main entry point for 'flask run' or 'python -m backend.app'
app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    
    print(f"TimeNest server starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
