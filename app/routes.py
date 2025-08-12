from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)

print("sys.path in routes.py:", sys.path)
print("Current directory:", os.getcwd())
print("Checking for app/utils/__init__.py:", os.path.exists(os.path.join(os.path.dirname(__file__), "utils", "__init__.py")))
print("Checking for app/utils/file_processor.py:", os.path.exists(os.path.join(os.path.dirname(__file__), "utils", "file_processor.py")))

try:
    from .utils.file_processor import extract_text_from_file
    print("Successfully imported extract_text_from_file")
except ImportError as e:
    print(f"Failed to import utils.file_processor: {e}")
    raise

try:
    from .models.resume_parser import parse_resume
    from .models.db_models import save_resume_to_db
    print("Successfully imported models")
except ImportError as e:
    print(f"Failed to import models: {e}")
    raise

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@main.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        logger.error("No file uploaded")
        return render_template("error.html", message="No file uploaded"), 400
    
    file = request.files["resume"]
    if file.filename == "":
        logger.error("No file selected")
        return render_template("error.html", message="No file selected"), 400
    
    if not file.filename.lower().endswith(tuple(current_app.config["ALLOWED_EXTENSIONS"])):
        logger.error(f"Unsupported file format: {file.filename}")
        return render_template("error.html", message="Unsupported file format. Use PDF or DOCX."), 400
    
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    try:
        file.save(upload_path)
        logger.info(f"Saved file to {upload_path}")
        
        resume_text = extract_text_from_file(upload_path)
        logger.info(f"Extracted resume text length: {len(resume_text)}")
        
        with open("extracted_resume_text.txt", "w", encoding="utf-8") as f:
            f.write(resume_text)
        logger.info("Saved extracted text to extracted_resume_text.txt")
        
        parsed_data = parse_resume(resume_text)
        logger.info(f"Parsed data: {parsed_data}")
        
        if "error" in parsed_data:
            logger.error(f"Parsing error: {parsed_data['error']}")
            return render_template("error.html", message=parsed_data["error"]), 500
        
        resume_id = save_resume_to_db(parsed_data, filename)
        logger.info(f"Saved resume ID: {resume_id}")
        
        formatted_data = json.dumps(parsed_data, indent=2) if parsed_data else "{}"
        logger.info(f"Formatted data: {formatted_data}")
        
        return render_template("result.html", 
                             data=formatted_data, 
                             resume_id=resume_id, 
                             filename=filename)
    
    except Exception as e:
        logger.error(f"Error in upload_resume: {str(e)}")
        return render_template("error.html", message=str(e)), 500