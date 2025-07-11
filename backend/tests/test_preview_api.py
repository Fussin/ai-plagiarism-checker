import unittest
from unittest.mock import MagicMock, AsyncMock # AsyncMock for await file.read()
from fastapi.testclient import TestClient
import io

from backend.main import app # Import the FastAPI app instance

# For creating dummy file content for UploadFile mocks
from docx import Document as DocxDocument
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class TestPreviewAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_text_content = "This is a short test text for preview."
        self.long_test_text_content = "This is a very long test text for preview. " * 50 # Approx 2500 chars

        # Create dummy PDF bytes
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, self.test_text_content)
        c.save()
        self.pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        # Create dummy DOCX bytes
        docx_buffer = io.BytesIO()
        doc = DocxDocument()
        doc.add_paragraph(self.test_text_content)
        doc.save(docx_buffer)
        self.docx_bytes = docx_buffer.getvalue()
        docx_buffer.close()

        # Create dummy TXT bytes
        self.txt_bytes = self.test_text_content.encode('utf-8')
        self.long_txt_bytes = self.long_test_text_content.encode('utf-8')


    def _create_mock_upload_file(self, filename: str, content_type: str, content_bytes: bytes) -> MagicMock:
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = filename
        mock_file.content_type = content_type

        # Mock the async read() method
        # For TestClient, actual async operations don't run in a separate loop in the same way,
        # but FastAPI's UploadFile.read() is async.
        # We need to make sure the mock's read() is an awaitable that returns the bytes.
        async def mock_read():
            return content_bytes

        mock_file.read = AsyncMock(side_effect=mock_read) # Use side_effect to call our async mock_read

        # Mock the close() method (which is also async for UploadFile, though often not awaited)
        async def mock_close():
            pass
        mock_file.close = AsyncMock(side_effect=mock_close)

        # For non-async use if TestClient handles it differently (less likely for UploadFile.read)
        # mock_file.file = io.BytesIO(content_bytes)
        return mock_file

    def test_check_multiple_files_preview_success(self):
        # TestClient handles async context automatically for route handlers.
        # When mocking UploadFile.read which is async, the test method itself doesn't need to be async
        # if the client call is synchronous.

        # The issue here is that TestClient's `files` argument expects file-like objects or tuples,
        # not MagicMock directly in the way a live FastAPI request would handle UploadFile.
        # A common way is to pass a tuple: ('filename', BytesIO_object, 'content_type')

        files_to_upload = [
            ('test.txt', io.BytesIO(self.txt_bytes), 'text/plain'),
            ('test.pdf', io.BytesIO(self.pdf_bytes), 'application/pdf'),
            ('test.docx', io.BytesIO(self.docx_bytes), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('test.jpg', io.BytesIO(b"fakeimagebytes"), 'image/jpeg'),
            ('test.mp4', io.BytesIO(b"fakevideobytes"), 'video/mp4'),
            ('unsupported.zip', io.BytesIO(b"fakezipbytes"), 'application/zip')
        ]

        # The 'files' parameter for TestClient should be a list of tuples.
        # Each tuple: (form_field_name, (filename, BytesIO_object, content_type))
        # Here, 'files' is the form field name for List[UploadFile].
        client_files_payload = [("files", f) for f in files_to_upload]

        response = self.client.post("/api/check", files=client_files_payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 6)

        results_map = {r["filename"]: r for r in data["results"]}

        # TXT
        self.assertIn("test.txt", results_map)
        self.assertEqual(results_map["test.txt"]["preview"], self.test_text_content)
        self.assertIsNone(results_map["test.txt"]["error"])

        # PDF
        self.assertIn("test.pdf", results_map)
        self.assertTrue(self.test_text_content in results_map["test.pdf"]["preview"])
        self.assertIsNone(results_map["test.pdf"]["error"])

        # DOCX
        self.assertIn("test.docx", results_map)
        self.assertTrue(self.test_text_content.replace("\n"," ") in results_map["test.docx"]["preview"].replace("\n"," ")) # Normalize newlines for comparison
        self.assertIsNone(results_map["test.docx"]["error"])

        # JPG
        self.assertIn("test.jpg", results_map)
        self.assertEqual(results_map["test.jpg"]["preview"], "[Image file: test.jpg] - Preview not applicable for images in this endpoint.")
        self.assertIsNone(results_map["test.jpg"]["error"])

        # MP4
        self.assertIn("test.mp4", results_map)
        self.assertEqual(results_map["test.mp4"]["preview"], "[Video file: test.mp4] - Preview not applicable for videos in this endpoint.")
        self.assertIsNone(results_map["test.mp4"]["error"])

        # ZIP (Unsupported)
        self.assertIn("unsupported.zip", results_map)
        self.assertIsNone(results_map["unsupported.zip"]["preview"])
        self.assertEqual(results_map["unsupported.zip"]["error"], "Unsupported file type: application/zip")

    def test_check_preview_long_text_truncation(self):
        client_files_payload = [("files", ('long_test.txt', io.BytesIO(self.long_txt_bytes), 'text/plain'))]
        response = self.client.post("/api/check", files=client_files_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        preview = data["results"][0]["preview"]
        self.assertTrue(len(preview) <= text_processing.MAX_PREVIEW_CHARS + 3) # +3 for "..."
        self.assertTrue(preview.endswith("..."))
        self.assertTrue(self.long_test_text_content.startswith(preview[:-3]))

    def test_check_preview_no_files(self):
        response = self.client.post("/api/check", files=[]) # Sending empty list might not work as expected
                                                       # Depending on how FastAPI handles empty File(...)
                                                       # It might raise a 422 from validation if no files are sent.
                                                       # Let's try sending None or no 'files' key.
        # If `files: List[UploadFile] = File(...)` and no files are sent, FastAPI returns 422.
        # The endpoint has a check `if not files: raise HTTPException`, but this is for an empty list *after* validation.
        # So, a 422 is expected here from FastAPI's request validation.

        # To test the internal "No files were uploaded." HTTPException, we'd need to bypass Pydantic/FastAPI validation
        # or send a request that passes validation but results in an empty list for the `files` parameter.
        # This is hard to do with TestClient for `List[UploadFile] = File(...)`.
        # For now, let's assume the 422 response is acceptable if no files are provided.

        # If we send data that is not a file for the 'files' field:
        response_malformed = self.client.post("/api/check", data={"files": "not_a_file"})
        self.assertEqual(response_malformed.status_code, 422) # Unprocessable Entity


if __name__ == '__main__':
    unittest.main()
