from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json # To serialize list fields for DB storage

from backend import models # Pydantic schemas & SQLAlchemy models
from backend.database import get_db
from backend.dependencies import get_current_active_user

router = APIRouter(
    prefix="/history",
    tags=["history"],
    dependencies=[Depends(get_current_active_user)] # All routes here require authentication
)

@router.post("/", response_model=models.ScanHistorySchema, status_code=status.HTTP_201_CREATED)
async def create_scan_history_entry(
    history_entry_in: models.ScanHistoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user)
):
    """
    Create a new scan history entry for the currently authenticated user.
    """
    db_history_entry = models.ScanHistoryDB(
        user_id=current_user.id,
        content_type=history_entry_in.content_type,
        file_name=history_entry_in.file_name,
        input_snippet=history_entry_in.input_snippet,
        originality_score=history_entry_in.originality_score,
        matched_sources_json=json.dumps(history_entry_in.matched_sources),
        rewrite_suggestions_json=json.dumps(history_entry_in.rewrite_suggestions)
    )
    db.add(db_history_entry)
    db.commit()
    db.refresh(db_history_entry)

    # Prepare the response by parsing JSON strings back to lists
    # This is necessary because the Pydantic model expects lists, not JSON strings.
    # A more robust solution might involve custom Pydantic validators or SQLAlchemy TypeDecorators for JSON.
    response_data = db_history_entry.__dict__ # Get all attributes
    response_data["matched_sources"] = json.loads(db_history_entry.matched_sources_json) if db_history_entry.matched_sources_json else []
    response_data["rewrite_suggestions"] = json.loads(db_history_entry.rewrite_suggestions_json) if db_history_entry.rewrite_suggestions_json else []

    return models.ScanHistorySchema.model_validate(response_data) # Pydantic v2


@router.get("/", response_model=List[models.ScanHistorySchema])
async def read_scan_history_for_user(
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user),
    skip: int = 0, # For pagination
    limit: int = 100 # For pagination
):
    """
    Retrieve scan history for the currently authenticated user, ordered by most recent.
    """
    history_entries_db = (
        db.query(models.ScanHistoryDB)
        .filter(models.ScanHistoryDB.user_id == current_user.id)
        .order_by(models.ScanHistoryDB.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Process entries to convert JSON strings back to lists for Pydantic validation
    processed_entries = []
    for entry_db in history_entries_db:
        entry_data = entry_db.__dict__
        entry_data["matched_sources"] = json.loads(entry_db.matched_sources_json) if entry_db.matched_sources_json else []
        entry_data["rewrite_suggestions"] = json.loads(entry_db.rewrite_suggestions_json) if entry_db.rewrite_suggestions_json else []
        processed_entries.append(models.ScanHistorySchema.model_validate(entry_data))

    return processed_entries
