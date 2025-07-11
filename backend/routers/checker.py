from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from typing import List
import shutil
import os

from ..config import settings
from ..models import TextCheckRequest, PlagiarismResult
# from ..dependencies import get_current_user # To protect routes
from ..services import text_processing, image_processing, video_processing, nlp_tasks

router = APIRouter(
    prefix="/check",
    tags=["checker"],
    # dependencies=[Depends(get_current_user)] # Uncomment to protect all routes in this router
)

# --- Text Checking ---
@router.post("/text", response_model=PlagiarismResult)
async def check_text_plagiarism(request: TextCheckRequest):
    if not request.text.strip():
        return PlagiarismResult(originality_score=1.0, matched_sources=["No text provided."], rewrite_suggestions=[])

    similarity_results = nlp_tasks.check_text_similarity_self(request.text)
    originality_score = similarity_results["originality_score"]
    matched_sources = []
    rewrite_suggestions = []

    if similarity_results["message"]:
        matched_sources.append(f"NLP Analysis: {similarity_results['message']}")

    if similarity_results["similar_pairs"]:
        for pair in similarity_results["similar_pairs"]:
            msg = (f"High similarity ({pair['similarity'] * 100:.1f}%) found between: "
                   f"'{pair['sentence1_text'][:50]}...' and '{pair['sentence2_text'][:50]}...'")
            matched_sources.append(msg)
        if "Consider rephrasing highly similar sentences." not in rewrite_suggestions:
             rewrite_suggestions.append("Consider rephrasing highly similar sentences.")


    if "copy" in request.text.lower(): # Check for keyword "copy"
        originality_score = min(originality_score, 0.6) # Potentially lower score
        matched_sources.append("Keyword 'copy' detected.")
        if "If using keywords like 'copy', ensure the content is original or properly cited." not in rewrite_suggestions:
            rewrite_suggestions.append("If using keywords like 'copy', ensure the content is original or properly cited.")

    return PlagiarismResult(
        originality_score=originality_score,
        matched_sources=matched_sources,
        rewrite_suggestions=rewrite_suggestions
    )

# --- File Upload and Processing (Common Utilities) ---
def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    os.makedirs(destination_folder, exist_ok=True)
    safe_filename = os.path.basename(upload_file.filename)
    if not safe_filename:
        safe_filename = f"uploaded_file_{os.urandom(4).hex()}"
    file_path = os.path.join(destination_folder, safe_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

# --- Text File Checking ---
@router.post("/file", response_model=PlagiarismResult)
async def check_text_file_plagiarism(file: UploadFile = File(...)):
    allowed_text_types = [
        "text/plain", "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"
    ]
    if file.content_type not in allowed_text_types:
        raise HTTPException(status_code=400, detail=f"Unsupported text file type: {file.content_type}. Supported: .txt, .pdf, .doc, .docx")

    temp_file_path = save_upload_file(file, settings.UPLOAD_DIR)
    rewrite_suggestions = []
    try:
        extracted_text = text_processing.extract_text(temp_file_path, file.content_type)
        if not extracted_text or not extracted_text.strip():
            return PlagiarismResult(originality_score=1.0, matched_sources=[f"No text could be extracted from {file.filename} or file is empty."], rewrite_suggestions=rewrite_suggestions)

        similarity_results = nlp_tasks.check_text_similarity_self(extracted_text)
        originality_score = similarity_results["originality_score"]
        matched_sources = []

        if similarity_results["message"]:
            matched_sources.append(f"NLP Analysis from '{file.filename}': {similarity_results['message']}")

        if similarity_results["similar_pairs"]:
            for pair in similarity_results["similar_pairs"]:
                msg = (f"High similarity ({pair['similarity'] * 100:.1f}%) in '{file.filename}' between: "
                       f"'{pair['sentence1_text'][:50]}...' and '{pair['sentence2_text'][:50]}...'")
                matched_sources.append(msg)
            if "Consider rephrasing highly similar sentences from the file." not in rewrite_suggestions:
                 rewrite_suggestions.append("Consider rephrasing highly similar sentences from the file.")

        if "copy" in extracted_text.lower():
            originality_score = min(originality_score, 0.6)
            matched_sources.append(f"Keyword 'copy' detected in {file.filename}.")
            if "If using keywords like 'copy' in the file, ensure the content is original or properly cited." not in rewrite_suggestions:
                rewrite_suggestions.append("If using keywords like 'copy' in the file, ensure the content is original or properly cited.")

        return PlagiarismResult(originality_score=originality_score, matched_sources=matched_sources, rewrite_suggestions=rewrite_suggestions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing text file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Image Checking ---
@router.post("/image", response_model=PlagiarismResult)
async def check_image_plagiarism(file: UploadFile = File(...)):
    allowed_image_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_image_types:
        raise HTTPException(status_code=400, detail=f"Unsupported image file type: {file.content_type}. Supported: .jpg, .png, .gif")

    temp_file_path = save_upload_file(file, settings.UPLOAD_DIR)
    originality_score = 1.0
    matched_sources = []
    rewrite_suggestions = []

    try:
        image_hash = image_processing.calculate_image_hash(temp_file_path)
        if image_hash:
            matched_sources.append(f"Image perceptual hash ({os.path.basename(file.filename)}): {image_hash}")
            mock_hits = image_processing.mock_reverse_image_search(image_hash)
            if mock_hits:
                originality_score = 0.1
                matched_sources.append(f"Potential plagiarism detected (mocked reverse image search):")
                for hit in mock_hits:
                    matched_sources.append(f"  - Found similar image at: {hit['url']} (Similarity: {hit['similarity']})")
                if "If this image is not original, consider replacing it or ensuring you have the rights to use it." not in rewrite_suggestions:
                    rewrite_suggestions.append("If this image is not original, consider replacing it or ensuring you have the rights to use it.")
            else:
                matched_sources.append("No direct matches found in mock reverse image search.")
        else:
            matched_sources.append(f"Could not calculate perceptual hash for image {os.path.basename(file.filename)}.")
            originality_score = 0.5

        return PlagiarismResult(originality_score=originality_score, matched_sources=matched_sources, rewrite_suggestions=rewrite_suggestions)
    except Exception as e:
        print(f"Error processing image {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Video Checking ---
MAX_FRAMES_TO_CHECK = 5
FRAME_INTERVAL_SECONDS = 5

@router.post("/video", response_model=PlagiarismResult)
async def check_video_plagiarism(file: UploadFile = File(...)):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Unsupported video file type. Only .mp4 is supported for now.")

    temp_video_path = save_upload_file(file, os.path.join(settings.UPLOAD_DIR, "videos_raw"))
    video_basename = os.path.basename(file.filename)

    processing_id = f"{os.path.splitext(video_basename)[0]}_{os.urandom(4).hex()}"
    frames_output_folder = os.path.join(settings.UPLOAD_DIR, "frames", processing_id)
    audio_output_file = os.path.join(settings.UPLOAD_DIR, "audio", f"{processing_id}.wav")

    os.makedirs(frames_output_folder, exist_ok=True)
    os.makedirs(os.path.dirname(audio_output_file), exist_ok=True)

    visual_originality_score = 1.0
    audio_originality_score = 1.0
    found_visual_plagiarism = False
    found_audio_plagiarism = False

    matched_sources = [f"Video file '{video_basename}' received for processing."]
    rewrite_suggestions = []

    try:
        # 1. Audio Processing
        extracted_audio_path = video_processing.extract_audio(temp_video_path, audio_output_file)
        transcribed_text = ""
        if extracted_audio_path:
            transcribed_text = video_processing.transcribe_audio_placeholder(extracted_audio_path)
            matched_sources.append(f"Audio extracted to: {os.path.basename(audio_output_file)}")
            if transcribed_text:
                matched_sources.append(f"Audio transcription (placeholder): '{transcribed_text[:100]}...'")
                audio_similarity_results = nlp_tasks.check_text_similarity_self(transcribed_text)
                audio_originality_score = audio_similarity_results["originality_score"]
                if audio_similarity_results["message"]:
                     matched_sources.append(f"Audio NLP: {audio_similarity_results['message']}")
                if audio_similarity_results["similar_pairs"]:
                    for pair in audio_similarity_results["similar_pairs"]:
                        found_audio_plagiarism = True
                        matched_sources.append(f"High audio similarity ({pair['similarity']*100:.1f}%): '{pair['sentence1_text'][:30]}...' and '{pair['sentence2_text'][:30]}...'")
                    if "Consider rephrasing similar segments in the audio transcription." not in rewrite_suggestions:
                        rewrite_suggestions.append("Consider rephrasing similar segments in the audio transcription.")
            else:
                matched_sources.append("Audio transcribed to empty text.")
        else:
            matched_sources.append("No audio could be extracted or extraction failed.")

        # 2. Visual Processing (Frames)
        extracted_frame_paths = video_processing.extract_frames(temp_video_path, frames_output_folder, frame_interval=FRAME_INTERVAL_SECONDS)

        if extracted_frame_paths:
            matched_sources.append(f"Extracted {len(extracted_frame_paths)} frames at {FRAME_INTERVAL_SECONDS}s interval.")
            frames_to_check_paths = extracted_frame_paths[:MAX_FRAMES_TO_CHECK]

            if frames_to_check_paths:
                matched_sources.append(f"Analyzing up to {len(frames_to_check_paths)} frames for visual content...")

            for i, frame_path in enumerate(frames_to_check_paths):
                frame_basename = os.path.basename(frame_path)
                frame_hash = image_processing.calculate_image_hash(frame_path)
                if frame_hash:
                    mock_hits = image_processing.mock_reverse_image_search(frame_hash)
                    if mock_hits:
                        found_visual_plagiarism = True
                        visual_originality_score = min(visual_originality_score, 0.1)
                        matched_sources.append(f"  - Frame {i+1} ({frame_basename}): Potential plagiarism (mocked reverse search):")
                        for hit in mock_hits:
                            matched_sources.append(f"    - Source: {hit['url']} (Similarity: {hit['similarity']})")
                        if "If video frames match external sources, ensure originality or rights, or replace the segment." not in rewrite_suggestions:
                             rewrite_suggestions.append("If video frames match external sources, ensure originality or rights, or replace the segment.")
            if not found_visual_plagiarism and frames_to_check_paths: # Only add if we actually checked frames
                 matched_sources.append("No direct visual matches found for analyzed frames in mock reverse search.")
        else:
            matched_sources.append("No frames extracted or frame extraction failed.")

        final_originality_score = min(visual_originality_score, audio_originality_score)
        if found_visual_plagiarism or found_audio_plagiarism: # If any type of plagiarism is found
            final_originality_score = min(final_originality_score, 0.2)

        return PlagiarismResult(originality_score=final_originality_score, matched_sources=matched_sources, rewrite_suggestions=rewrite_suggestions)

    except Exception as e:
        print(f"Error processing video {video_basename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video '{video_basename}': {str(e)}")
    finally:
        if os.path.exists(temp_video_path): os.remove(temp_video_path)
        if os.path.exists(frames_output_folder): shutil.rmtree(frames_output_folder)
        if os.path.exists(audio_output_file): os.remove(audio_output_file)
