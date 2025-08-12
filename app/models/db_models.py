from pymongo import MongoClient
from datetime import datetime
from config import Config

def save_resume_to_db(parsed_data, filename):
    client = MongoClient(Config.MONGO_URI)
    db = client["resume_parser"]
    collection = db["resumes"]
    
    resume_doc = {
        "name": parsed_data.get("Name"),
        "email": parsed_data.get("Email"),
        "state": parsed_data.get("State"),
        "address": parsed_data.get("Address"),
        "education": parsed_data.get("Education", []),
        "skills": parsed_data.get("Skills", []),
        "technical_skills": parsed_data.get("Technical Skills", []),
        "experience": parsed_data.get("Experience", []),
        "certifications": parsed_data.get("Certifications", []),
        "filename": filename,
        "created_at": datetime.utcnow()
    }
    
    result = collection.insert_one(resume_doc)
    client.close()
    return str(result.inserted_id)