from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_active_user
from backend.plans import get_plan_limits
from backend.services import usage_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)]
)

class UsageSummaryResponse(models.BaseModel):
    plan: str
    words_scanned: int
    word_limit: int
    humanizer_uses: int
    humanizer_limit: int

@router.get("/me/usage-summary", response_model=UsageSummaryResponse)
async def get_user_usage_summary(
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user)
):
    """
    Retrieves the current user's usage summary and plan limits.
    """
    plan_limits = get_plan_limits(current_user.plan)
    usage = usage_service.get_or_create_usage_record(db, current_user)

    word_limit = plan_limits.get("monthly_word_limit", 0)
    humanizer_usage_percent = plan_limits.get("humanizer_usage_percent", 0)

    # Handle infinite limits for display
    if word_limit == float('inf'):
        word_limit = -1 # Use -1 to signify "unlimited" to the frontend

    humanizer_limit = int(word_limit * humanizer_usage_percent) if word_limit != -1 else -1

    return UsageSummaryResponse(
        plan=current_user.plan,
        words_scanned=usage.words_scanned,
        word_limit=word_limit,
        humanizer_uses=usage.humanizer_uses,
        humanizer_limit=humanizer_limit
    )
