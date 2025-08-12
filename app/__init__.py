from flask import Flask
import os
import sys

def create_app():
    app = Flask(__name__)
    
    # Debug: Print sys.path
    print("sys.path in __init__.py:", sys.path)
    
    # Load config from config.py in the project root
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.append(project_root)
        from config import Config
        app.config.from_object(Config)
        print("Config loaded successfully:")
        print("UPLOAD_FOLDER:", app.config.get("UPLOAD_FOLDER"))
        print("MONGO_URI:", app.config.get("MONGO_URI"))
        print("HUGGINGFACE_API_KEY:", app.config.get("HUGGINGFACE_API_KEY"))
    except ImportError as e:
        print(f"Failed to import config: {e}")
        app.config.update(
            SECRET_KEY="your-secret-key",
            MONGO_URI="mongodb://localhost:27017/resume_parser",
            HUGGINGFACE_API_KEY=None,
            UPLOAD_FOLDER="app/static/uploads",
            ALLOWED_EXTENSIONS={".pdf", ".docx"}
        )
        print("Using fallback configuration")
    
    # Create upload folder if it doesn't exist
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        print(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")
    except Exception as e:
        print(f"Failed to create upload folder: {e}")
        raise
    
    # Debug: Check template folder
    template_folder = os.path.join(os.path.dirname(__file__), "templates")
    print("Template folder:", template_folder)
    print("Template folder exists:", os.path.exists(template_folder))
    print("index.html exists:", os.path.exists(os.path.join(template_folder, "index.html")))
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app