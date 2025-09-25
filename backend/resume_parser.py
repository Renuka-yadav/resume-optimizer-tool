import re
from pdfminer.high_level import extract_text
import docx2txt

def extract_resume_text(file_path):
    """
    Extracts text from a resume file (PDF or DOCX).
    Returns an empty string if no text can be extracted.
    """
    text = ""
    if file_path.endswith(".pdf"):
        text = extract_text(file_path)
    elif file_path.endswith(".docx"):
        text = docx2txt.process(file_path)

    if text:
        # Clean up the text by removing extra whitespace
        # and ensure we don't call .group() on a None object
        match = re.search(r'[^\s].*[^\s]', text, re.DOTALL)
        if match:
            return match.group(0)

    return "" # Return an empty string if no text was found