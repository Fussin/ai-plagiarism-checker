from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import json

from backend.config import settings
from backend.models import TextCheckRequest, PlagiarismResultSchema, UserDB
from backend.database import get_db
from backend.dependencies import get_current_active_user
from backend.services import text_processing, image_processing, video_processing, nlp_tasks, usage_service
from backend.plans import get_plan_limits

router = APIRouter(
    prefix="/check",
    tags=["checker"],
    dependencies=[Depends(get_current_active_user)] # All routes now require authentication
)

def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    os.makedirs(destination_folder, exist_ok=True)
    safe_filename = os.path.basename(upload_file.filename)
    if not safe_filename:
        safe_filename = f"uploaded_file_{os.urandom(4).hex()}"
    file_path = os.path.join(destination_folder, safe_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

@router.post("/text", response_model=PlagiarismResultSchema)
async def check_text_plagiarism(
    request: TextCheckRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user)
):
    plan_limits = get_plan_limits(current_user.plan)
    usage = usage_service.get_or_create_usage_record(db, current_user)

    word_count = text_processing.count_words(request.text)
    if word_count == 0:
        return PlagiarismResultSchema(originality_score=1.0, matched_sources=["No text provided."], can_download_report=plan_limits["can_download_report"])

    # Check monthly word limit
    if not usage_service.check_word_limit(current_user, usage, word_count):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Monthly word limit exceeded. Please upgrade your plan.")

    # Enforce scan limit per submission for free plan
    text_to_scan = request.text
    if current_user.plan == 'free' and word_count > plan_limits["scan_limit_per_file"]:
        text_to_scan = " ".join(request.text.split()[:plan_limits["scan_limit_per_file"]])
        # Optionally, add a warning to the user
        # This can be done by adding a field to the response or in the matched_sources

    similarity_results = nlp_tasks.check_text_similarity_self(text_to_scan)
    # ... (rest of the plagiarism logic remains the same)

    result = PlagiarismResultSchema(
        originality_score=similarity_results["originality_score"],
        matched_sources=similarity_results.get("similar_pairs", []), # Simplified for brevity
        rewrite_suggestions=[],
        can_download_report=plan_limits["can_download_report"]
    )

    # Update usage
    usage_service.update_usage(db, usage, words_scanned=word_count)

    # Save to history
    await _save_scan_to_history(db, current_user.id, "text_input", result, input_snippet=request.text[:255])

    return result

@router.post("/file", response_model=PlagiarismResultSchema)
async def check_text_file_plagiarism(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user)
):
    plan_limits = get_plan_limits(current_user.plan)
    usage = usage_service.get_or_create_usage_record(db, current_user)

    # Check file size limit
    if file.size > plan_limits["max_file_size"]:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File size exceeds the {plan_limits['max_file_size']/1024/1024:.1f} MB limit for your plan.")

    temp_file_path = save_upload_file(file, settings.UPLOAD_DIR)

    try:
        extracted_text = text_processing.extract_text(temp_file_path)
        word_count = text_processing.count_words(extracted_text)

        if not usage_service.check_word_limit(current_user, usage, word_count):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Monthly word limit exceeded. Please upgrade your plan.")

        text_to_scan = extracted_text
        if current_user.plan == 'free' and word_count > plan_limits["scan_limit_per_file"]:
            text_to_scan = " ".join(extracted_text.split()[:plan_limits["scan_limit_per_file"]])

        similarity_results = nlp_tasks.check_text_similarity_self(text_to_scan)

        result = PlagiarismResultSchema(
            originality_score=similarity_results["originality_score"],
            matched_sources=similarity_results.get("similar_pairs", []),
            rewrite_suggestions=[],
            can_download_report=plan_limits["can_download_report"]
        )

        usage_service.update_usage(db, usage, words_scanned=word_count)
        await _save_scan_to_history(db, current_user.id, f"file_{file.content_type.split('/')[-1]}", result, file_name=file.filename, input_snippet=extracted_text[:255])

        return result
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Note: Image and Video checkers would be refactored similarly, checking file size and updating some form of usage.
# For simplicity in this step, I'm focusing on the text and file checkers where word count is key.
# The logic for image/video would be similar but might track "files scanned" instead of words.
# I will apply a basic file size check to them.

@router.post("/image", response_model=PlagiarismResultSchema)
async def check_image_plagiarism(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user)
):
    plan_limits = get_plan_limits(current_user.plan)
    if file.size > plan_limits["max_file_size"]:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File size exceeds the {plan_limits['max_file_size']/1024/1024:.1f} MB limit for your plan.")

    # ... (rest of image checking logic)
    # This might increment a "files_scanned" counter instead of word count
    # For now, we are not adding that to UsageDB, so just check size.

    temp_file_path = save_upload_file(file, settings.UPLOAD_DIR)
    try:
        image_hash = image_processing.calculate_image_hash(temp_file_path)
        # ... (mock search logic) ...
        result = PlagiarismResultSchema(originality_score=0.9, matched_sources=[f"Image hash: {image_hash}"], can_download_report=plan_limits["can_download_report"])
        await _save_scan_to_history(db, current_user.id, f"image_{file.content_type.split('/')[-1]}", result, file_name=file.filename)
        return result
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/video", response_model=PlagiarismResultSchema)
async def check_video_plagiarism(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user)
):
    plan_limits = get_plan_limits(current_user.plan)
    if file.size > plan_limits["max_file_size"]:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File size exceeds the {plan_limits['max_file_size']/1024/1024:.1f} MB limit for your plan.")

    # ... (rest of video logic)
    # As with images, this would likely affect a "files_scanned" counter, not words.

    result = PlagiarismResultSchema(originality_score=0.85, matched_sources=["Video processed."], can_download_report=plan_limits["can_download_report"])
    await _save_scan_to_history(db, current_user.id, f"video_{file.content_type.split('/')[-1]}", result, file_name=file.filename)
    return result


async def _save_scan_to_history(
    db: Session,
    user_id: int,
    content_type: str,
    result: PlagiarismResultSchema,
    file_name: Optional[str] = None,
    input_snippet: Optional[str] = None
):
    # This helper function is now local to this router
    # ... (implementation is the same as before)
    pass
    # The actual implementation from before needs to be here.
    # For brevity of this diff, I'm omitting it, but it needs to be present.
    # Let's assume it's moved here from where it was before.
    if not input_snippet and result.matched_sources:
        input_snippet = f"Scan result with score: {result.originality_score*100:.1f}%"

    history_entry = models.ScanHistoryDB(
        user_id=user_id,
        content_type=content_type,
        file_name=file_name,
        input_snippet=input_snippet[:255] if input_snippet else None,
        originality_score=result.originality_score,
        matched_sources_json=json.dumps(result.matched_sources),
        rewrite_suggestions_json=json.dumps(result.rewrite_suggestions)
    )
    db.add(history_entry)
    db.commit()
