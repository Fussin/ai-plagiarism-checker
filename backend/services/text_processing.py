# Functions for processing text, e.g., extracting text from files

from pdfminer.high_level import extract_text as extract_text_from_pdf
import docx

def extract_text(filepath: str, mimetype: str) -> str:
    """
    Extracts text content from various file types.
    """
    if mimetype == "application/pdf":
        return extract_text_from_pdf(filepath)
    elif mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    elif mimetype == "text/plain":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type for text extraction: {mimetype}")

# More text processing functions (e.g., cleaning, tokenization) can be added here.
