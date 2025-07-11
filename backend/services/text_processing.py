import io
from pdfminer.high_level import extract_text as pdfminer_extract_text_from_fp # Renamed for clarity
import docx

# --- Existing filepath-based extraction (used by /check/* routes) ---

def extract_text_from_filepath(filepath: str, mimetype: str) -> str:
    """
    Extracts text content from various file types using a filepath.
    """
    if mimetype == "application/pdf":
        try:
            return pdfminer_extract_text_from_fp(filepath)
        except Exception as e:
            print(f"Error extracting text from PDF filepath {filepath}: {e}")
            raise ValueError(f"Could not extract text from PDF: {e}")
    elif mimetype in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]: # Handle .doc as well, though python-docx is mainly for .docx
        try:
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            # python-docx might fail on older .doc formats.
            print(f"Error extracting text from DOCX/DOC filepath {filepath}: {e}")
            raise ValueError(f"Could not extract text from Word document: {e}")
    elif mimetype == "text/plain":
        try:
            with open(filepath, "r", encoding="utf-8") as f: # Specify encoding
                return f.read()
        except Exception as e:
            print(f"Error reading text file {filepath}: {e}")
            raise ValueError(f"Could not read text file: {e}")
    else:
        raise ValueError(f"Unsupported file type for text extraction via filepath: {mimetype}")


# --- New bytes-based extraction functions (for /api/check preview route) ---

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes."""
    try:
        return pdfminer_extract_text_from_fp(io.BytesIO(file_bytes))
    except Exception as e:
        print(f"Error extracting text from PDF bytes: {e}")
        # Consider returning empty string or specific error for preview endpoint
        return f"[Error extracting PDF content: {str(e)[:100]}]"

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    """Extracts text from DOCX bytes."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from DOCX bytes: {e}")
        return f"[Error extracting DOCX content: {str(e)[:100]}]"

def extract_text_from_txt_bytes(file_bytes: bytes) -> str:
    """Extracts text from TXT bytes."""
    try:
        # Try common encodings; UTF-8 is a good default.
        # For a robust solution, encoding detection might be needed, but that's complex.
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_bytes.decode('latin-1') # Try another common one
        except Exception as e:
            print(f"Error decoding TXT bytes: {e}")
            return f"[Error decoding TXT content: {str(e)[:100]}]"
    except Exception as e: # Catch other potential errors
        print(f"Error processing TXT bytes: {e}")
        return f"[Error processing TXT content: {str(e)[:100]}]"


# The original extract_text function is renamed to extract_text_from_filepath
# to avoid confusion. The /check/* routes in checker.py should be updated if they
# were calling a function named just `extract_text`.
# Let's check checker.py - it was using `text_processing.extract_text`.
# So, I should keep an `extract_text` alias or rename calls in checker.py.
# For now, I'll rename the old one and the new /api/check will call the _bytes functions.
# The existing /check/file endpoint in checker.py uses the filepath method.

# To maintain compatibility with existing checker.py:
extract_text = extract_text_from_filepath
# This way, checker.py doesn't need to change its call to text_processing.extract_text
