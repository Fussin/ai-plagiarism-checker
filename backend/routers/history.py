from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_active_user
from backend.plans import get_plan_limits # Import plan limits

router = APIRouter(
    prefix="/history",
    tags=["history"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=models.ScanHistorySchema, status_code=status.HTTP_201_CREATED)
async def create_scan_history_entry(
    history_entry_in: models.ScanHistoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user)
):
    """
    Create a new scan history entry for the currently authenticated user.
    This endpoint is called internally by the checker routes.
    The main check for history access is on the GET endpoint.
    """
    plan_limits = get_plan_limits(current_user.plan)
    if not plan_limits["can_view_history"]:
        # Don't save history if the user's plan doesn't allow viewing it.
        # This prevents cluttering the DB with inaccessible data.
        # Silently fail here, as the user got their scan result, which is the primary feature.
        # The frontend will know not to even try to save history based on the plan.
        # Or raise an error if this endpoint were to be called directly by a savvy user.
        # For now, we'll just not save it.
        print(f"User {current_user.email} on '{current_user.plan}' plan. History not saved.")
        # To satisfy the response model, we can return a "dummy" but unsaved object.
        # A better approach is to not call this endpoint at all from the checker logic for free users.
        # Let's assume the checker logic will be updated to not call this.
        # If it is called, we can raise an error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your plan does not support saving history.")

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

    response_data = db_history_entry.__dict__
    response_data["matched_sources"] = json.loads(db_history_entry.matched_sources_json) if db_history_entry.matched_sources_json else []
    response_data["rewrite_suggestions"] = json.loads(db_history_entry.rewrite_suggestions_json) if db_history_entry.rewrite_suggestions_json else []

    return models.ScanHistorySchema.model_validate(response_data)


@router.get("/", response_model=List[models.ScanHistorySchema])
async def read_scan_history_for_user(
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve scan history for the currently authenticated user.
    Access is forbidden for users on the 'free' plan.
    """
    plan_limits = get_plan_limits(current_user.plan)
    if not plan_limits["can_view_history"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to scan history is not available on your current plan. Please upgrade.")

    history_entries_db = (
        db.query(models.ScanHistoryDB)
        .filter(models.ScanHistoryDB.user_id == current_user.id)
        .order_by(models.ScanHistoryDB.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    processed_entries = []
    for entry_db in history_entries_db:
        entry_data = entry_db.__dict__
        entry_data["matched_sources"] = json.loads(entry_db.matched_sources_json) if entry_db.matched_sources_json else []
        entry_data["rewrite_suggestions"] = json.loads(entry_db.rewrite_suggestions_json) if entry_db.rewrite_suggestions_json else []
        processed_entries.append(models.ScanHistorySchema.model_validate(entry_data))

    return processed_entries
