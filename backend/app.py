import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv


def create_app():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)

    # Point Flask to frontend folder for static files and templates
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    app = Flask(__name__, 
                static_folder=frontend_dir,
                static_url_path="",
                template_folder=frontend_dir)
    app.config.from_object("backend.config.Config")

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    JWTManager(app)

    # Initialize DB teardown hooks
    from backend.utils.db import init_app as init_db

    init_db(app)

    # Register blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.task_routes import tasks_bp
    from backend.routes.habit_routes import habits_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")

    # Serve frontend pages
    @app.get("/")
    def index():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, "index.html")
    
    @app.get("/<path:path>")
    def serve_static(path):
        from flask import send_from_directory
        # Serve files from frontend folder
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # If not found, try adding .html extension
        if os.path.exists(os.path.join(app.static_folder, f"{path}.html")):
            return send_from_directory(app.static_folder, f"{path}.html")
        return jsonify(error="Not Found"), 404

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="Time Nest API"), 200

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not Found"), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify(error="Internal Server Error"), 500

    return app


# Instantiate app for 'flask --app backend.app run'
app = create_app()


if __name__ == "__main__":
    # Direct run support: python -m backend.app
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )
