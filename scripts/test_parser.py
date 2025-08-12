from app.models.resume_parser import parse_resume
from app.utils.file_processor import extract_text_from_file

# Test the parser with a sample resume
resume_text = extract_text_from_file("data/sample_resumes/resume1.pdf")
parsed_data = parse_resume(resume_text)
print(parsed_data)