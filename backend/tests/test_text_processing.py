import unittest
import os
from backend.services.text_processing import extract_text
from backend.config import settings # To use settings.UPLOAD_DIR or a dedicated test_data dir

# For creating dummy docx and pdf files for testing
from docx import Document as DocxDocument
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class TestTextProcessing(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files if it doesn't exist
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Content for test files
        self.test_content = "This is a test sentence.\nAnother line for testing."

        # Create a dummy .txt file
        self.txt_filepath = os.path.join(self.test_data_dir, "test_document.txt")
        with open(self.txt_filepath, "w", encoding="utf-8") as f:
            f.write(self.test_content)

        # Create a dummy .docx file
        self.docx_filepath = os.path.join(self.test_data_dir, "test_document.docx")
        doc = DocxDocument()
        doc.add_paragraph(self.test_content.split('\n')[0])
        doc.add_paragraph(self.test_content.split('\n')[1])
        doc.save(self.docx_filepath)

        # Create a dummy .pdf file
        self.pdf_filepath = os.path.join(self.test_data_dir, "test_document.pdf")
        c = canvas.Canvas(self.pdf_filepath, pagesize=letter)
        textobject = c.beginText(100, 750) # x, y position from bottom-left
        for line in self.test_content.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        c.save()

    def tearDown(self):
        # Clean up created test files
        if os.path.exists(self.txt_filepath):
            os.remove(self.txt_filepath)
        if os.path.exists(self.docx_filepath):
            os.remove(self.docx_filepath)
        if os.path.exists(self.pdf_filepath):
            os.remove(self.pdf_filepath)
        # Potentially remove self.test_data_dir if it's empty and was created by setUp
        if os.path.exists(self.test_data_dir) and not os.listdir(self.test_data_dir):
            os.rmdir(self.test_data_dir)


    def test_extract_text_from_txt(self):
        extracted = extract_text(self.txt_filepath, "text/plain")
        self.assertEqual(extracted.strip(), self.test_content.strip())

    def test_extract_text_from_docx(self):
        extracted = extract_text(self.docx_filepath, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        # DOCX extraction might add extra newlines or have slightly different spacing
        self.assertIn("This is a test sentence.", extracted)
        self.assertIn("Another line for testing.", extracted)
        # A more robust check would normalize whitespace before comparison
        normalized_extracted = " ".join(extracted.split())
        normalized_original = " ".join(self.test_content.split())
        self.assertEqual(normalized_extracted, normalized_original)


    def test_extract_text_from_pdf(self):
        extracted = extract_text(self.pdf_filepath, "application/pdf")
        # PDF extraction can be tricky; exact string match is good, but sometimes contains artifacts.
        # For simple text like this, it should be fairly accurate.
        # pdfminer.six tends to add form feed characters (\f) or extra spaces sometimes.
        normalized_extracted = " ".join(extracted.replace('\f', ' ').split())
        normalized_original = " ".join(self.test_content.split())
        self.assertEqual(normalized_extracted.strip(), normalized_original.strip())

    def test_extract_text_unsupported_type(self):
        # Create a dummy unsupported file (e.g. a png renamed to .txt but with png mimetype)
        # For simplicity, we'll just pass a mimetype not handled
        with self.assertRaises(ValueError):
            extract_text(self.txt_filepath, "image/png") # Pass txt path but wrong mimetype

if __name__ == '__main__':
    # This allows running tests directly from this file
    # You might need to adjust Python's path if running from root or use `python -m unittest discover`

    # Ensure the test runner can find the 'backend' module.
    # This is often handled by running `python -m unittest discover -s backend/tests` from the project root.
    # Or by setting PYTHONPATH environment variable.
    # For direct execution from backend/tests:
    import sys
    # Add project root to sys.path if this script is run directly
    # and the backend module is not found.
    # This assumes backend/tests/ is one level down from project root.
    # Adjust as necessary if your structure is different.
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(current_dir)
    # sys.path.insert(0, project_root)

    unittest.main()
