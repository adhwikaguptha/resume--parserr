import re
from datetime import datetime

def validate_email(email):
    if not email:
        return None
    email = email.strip().lower()
    if re.match(r"^[a-zA-Z0.9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return email
    return None

def normalize_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%m/%Y").isoformat()
    except:
        return date_str