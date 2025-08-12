from affinda import AffindaAPI, TokenCredential
import time
import os

# Replace with your actual API key and workspace ID
API_KEY = "aff_c8811402988b06cf0a2cef113448bf4e04beeebe"
WORKSPACE_ID = "ZhWsAvdi"  # Example: "ZhWsAvdi"

# Initialize API client
credential = TokenCredential(API_KEY)
client = AffindaAPI(credential=credential)

# Path to your resume
resume_path = r"C:\\Users\\Admin\\Downloads\\adhwikaresume (6).pdf"
print(f"📤 Uploading {resume_path} to workspace {WORKSPACE_ID}...")

# Open the file and upload it
with open(resume_path, "rb") as file:
    document = client.create_document(file=file, collection=WORKSPACE_ID)

# Wait until the document is parsed
doc_id = document.id
print("⏳ Waiting for parsing to complete...")

while True:
    doc_status = client.get_document(doc_id)
    if doc_status.ready:
        break
    time.sleep(1)

print("✅ Parsing completed.\n")

# Extract and print parsed fields
parsed_data = doc_status.resume  # Only for resumes
if parsed_data:
    print(f"📄 Name: {parsed_data.name}")
    print(f"📧 Email(s): {parsed_data.emails}")
    print(f"📱 Phone: {parsed_data.phone_numbers}")
    print(f"🎓 Education: {[e.text for e in parsed_data.education]}")
    print(f"💼 Work Experience: {[e.text for e in parsed_data.work_experience]}")
else:
    print("⚠️ No resume data found in document.")

