import os
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_file(file_path):
    """
    Extract text from PDF or DOCX files, with OCR fallback for complex PDFs.
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Extracting text from {file_path} (extension: {file_ext})")
        
        if file_ext == ".pdf":
            # Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text(layout=True) or ""  # Preserve layout
                        text += page_text + "\n"
                    if len(text.strip()) > 50:  # Arbitrary threshold
                        logger.info(f"Extracted {len(text)} characters using pdfplumber")
                        logger.debug(f"Extracted text sample: {text[:200]}")
                        return text.strip()
                    else:
                        logger.warning(f"Insufficient text extracted with pdfplumber ({len(text)} chars), trying OCR")
            except Exception as e:
                logger.error(f"pdfplumber failed: {str(e)}")
            
            # Fallback to OCR
            try:
                images = convert_from_path(file_path, poppler_path=r"C:\Program Files\poppler\bin")  # Update path if needed
                text = ""
                for i, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    text += page_text + "\n"
                    logger.info(f"Extracted text from page {i+1} using OCR")
                if text.strip():
                    logger.info(f"Extracted {len(text)} characters using OCR")
                    logger.debug(f"OCR text sample: {text[:200]}")
                    return text.strip()
                else:
                    logger.error("OCR extracted no text")
                    raise ValueError("No text extracted from PDF")
            except Exception as e:
                logger.error(f"OCR failed: {str(e)}")
                raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        
        elif file_ext == ".docx":
            try:
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                logger.info(f"Extracted {len(text)} characters from DOCX")
                logger.debug(f"DOCX text sample: {text[:200]}")
                return text.strip()
            except Exception as e:
                logger.error(f"DOCX extraction failed: {str(e)}")
                raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
        
        else:
            logger.error(f"Unsupported file extension: {file_ext}")
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
    
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        raise