import requests
from config import Config
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_resume(resume_text):
    if not resume_text or not resume_text.strip():
        logger.error("Empty or invalid resume text provided")
        return {"error": "No text extracted from resume"}
    
    models = [
        "deepset/roberta-base-squad2",
        "bert-large-uncased-whole-word-masking-finetuned-squad"
    ]
    headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
    
    if not Config.HUGGINGFACE_API_KEY or Config.HUGGINGFACE_API_KEY.startswith("hf_") is False:
        logger.error("Invalid or missing Hugging Face API key")
        return {"error": "Invalid or missing Hugging Face API key"}
    
    questions = {
        "Name": "Who is the person named in the resume?",
        "Email": "What is the email address listed in the resume?",
        "State": "Which state is mentioned in the address?",
        "Address": "What is the full address?",
        "Education": "What is the educational background?",
        "Skills": "What skills are listed?",
        "Technical Skills": "What technical skills are listed?",
        "Experience": "What is the work experience history?",
        "Certifications": "What certifications are listed?"
    }
    
    parsed_data = {}
    
    for model in models:
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        logger.info(f"Attempting to parse with model: {model}")
        success = True
        
        for section, question in questions.items():
            if section in parsed_data and parsed_data[section]:
                continue  # Skip if already parsed
            payload = {
                "inputs": {
                    "question": question,
                    "context": resume_text[:2000]  # Increased context
                }
            }
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=10)
                logger.info(f"API response for {section}: status={response.status_code}, content={response.text}")
                if response.status_code == 200:
                    result = response.json()
                    score = result.get("score", 0)
                    answer = result.get("answer") if score > 0.0001 else None
                    parsed_data[section] = answer
                    logger.info(f"{section} score: {score}, answer: {answer}")
                elif response.status_code in (401, 403):
                    logger.error(f"API error for {section}: Unauthorized - Invalid API key or permissions")
                    return {"error": "Unauthorized - Invalid Hugging Face API key or permissions"}
                elif response.status_code == 429:
                    logger.error(f"Rate limit exceeded for {section}")
                    success = False
                    break
                else:
                    logger.error(f"API error for {section}: {response.status_code} - {response.text}")
                    parsed_data[section] = None
            except Exception as e:
                logger.error(f"Exception for {section}: {str(e)}")
                parsed_data[section] = None
        
        if success:
            break
    
    if not any(parsed_data.values()):
        logger.warning("No data parsed; trying regex fallback")
        parsed_data["Email"] = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resume_text)
        parsed_data["Email"] = parsed_data["Email"].group(0).lower() if parsed_data["Email"] else None
        name_match = re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+", resume_text, re.MULTILINE)
        parsed_data["Name"] = name_match.group(0) if name_match else None
    
    if parsed_data.get("Email") and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", parsed_data["Email"]):
        parsed_data["Email"] = None
    
    if parsed_data.get("Education"):
        education_entries = parsed_data["Education"].split(";")
        parsed_data["Education"] = [
            {
                "institution": e.split(",")[0].strip() if "," in e else e.strip(),
                "degree": e.split(",")[1].strip() if "," in e and len(e.split(",")) > 1 else None,
                "dates": e.split(",")[2].strip() if "," in e and len(e.split(",")) > 2 else None
            }
            for e in education_entries if e.strip()
        ]
    
    parsed_data["Skills"] = [s.strip() for s in parsed_data.get("Skills", "").split(",") if s.strip()] if parsed_data.get("Skills") else []
    parsed_data["Technical Skills"] = [s.strip() for s in parsed_data.get("Technical Skills", "").split(",") if s.strip()] if parsed_data.get("Technical Skills") else []
    
    if parsed_data.get("Experience"):
        experience_entries = parsed_data["Experience"].split(";")
        parsed_data["Experience"] = [
            {
                "company": e.split(",")[0].strip() if "," in e else e.strip(),
                "role": e.split(",")[1].strip() if "," in e and len(e.split(",")) > 1 else None,
                "dates": e.split(",")[2].strip() if "," in e and len(e.split(",")) > 2 else None
            }
            for e in experience_entries if e.strip()
        ]
    
    parsed_data["Certifications"] = [c.strip() for c in parsed_data.get("Certifications", "").split(",") if c.strip()] if parsed_data.get("Certifications") else []
    
    logger.info(f"Final parsed data: {parsed_data}")
    return parsed_data