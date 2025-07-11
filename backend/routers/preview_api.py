from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import List, Optional
import io

from backend import models # Pydantic schemas
from backend.services import text_processing # For byte-based text extraction

router = APIRouter(
    prefix="/api", # As per user request for /api/check
    tags=["preview"],
    # No global authentication for this endpoint as per current plan, can be added if needed
)

MAX_PREVIEW_CHARS = 500

@router.post("/check", response_model=models.FilePreviewResponse)
async def check_multiple_files_preview(files: List[UploadFile] = File(...)):
    """
    Accepts multiple files, attempts to extract text from supported types,
    and returns a preview (first 500 characters) or file type acknowledgment.
    """
    results: List[models.FilePreviewItem] = []

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files were uploaded.")

    for file in files:
        content_type = file.content_type
        filename = file.filename
        preview_text: Optional[str] = None
        error_message: Optional[str] = None

        try:
            file_bytes = await file.read() # Read file content as bytes

            if content_type == "application/pdf":
                preview_text = text_processing.extract_text_from_pdf_bytes(file_bytes)
            elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                preview_text = text_processing.extract_text_from_docx_bytes(file_bytes)
            elif content_type == "text/plain":
                preview_text = text_processing.extract_text_from_txt_bytes(file_bytes)
            elif content_type and content_type.startswith("image/"):
                preview_text = f"[Image file: {filename}] - Preview not applicable for images in this endpoint."
            elif content_type and content_type.startswith("video/"):
                preview_text = f"[Video file: {filename}] - Preview not applicable for videos in this endpoint."
            else:
                error_message = f"Unsupported file type: {content_type}"

            # Truncate preview_text if it was extracted and not an error message itself
            if preview_text and not error_message and not preview_text.startswith("[Error"):
                if len(preview_text) > MAX_PREVIEW_CHARS:
                    preview_text = preview_text[:MAX_PREVIEW_CHARS] + "..."
                elif not preview_text.strip(): # If extracted text is empty or whitespace
                    preview_text = "[Empty or whitespace content extracted]"


        except Exception as e:
            print(f"Error processing file {filename} ({content_type}): {e}")
            error_message = f"Error processing file: {str(e)}"
        finally:
            await file.close() # Ensure file is closed

        results.append(models.FilePreviewItem(
            filename=filename,
            content_type=str(content_type), # Ensure it's a string
            preview=preview_text,
            error=error_message
        ))

    return models.FilePreviewResponse(results=results)
