from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/resume_parser")
    HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
    UPLOAD_FOLDER = "app/static/uploads"
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}