from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
import sqlalchemy as sa # Import sqlalchemy
from typing import List

from backend import models
from backend.database import get_db
from backend.plans import PLAN_LIMITS
from backend.dependencies import get_current_admin_user # Import the admin dependency

router = APIRouter(
    prefix="/admin",
    tags=["admin_tools"],
    dependencies=[Depends(get_current_admin_user)] # Protect all routes in this router
)

@router.post("/set-plan/{user_id}", response_model=models.UserSchema)
async def set_user_plan(
    user_id: int,
    # Using Body to expect a payload like {"plan": "pro_basic"}
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    (Admin Mock) Sets the plan for a given user.
    This is for testing purposes only and has no real security.
    """
    new_plan = payload.get("plan")
    if not new_plan or new_plan not in PLAN_LIMITS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan specified. Available plans are: {list(PLAN_LIMITS.keys())}"
        )

    db_user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    print(f"ADMIN ACTION: Changing plan for user {db_user.email} from '{db_user.plan}' to '{new_plan}'.")
    db_user.plan = new_plan
    # You might also want to change subscription_status here, e.g., to 'active'
    db_user.subscription_status = 'active'

    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/reset-all-usage")
async def reset_all_usage(db: Session = Depends(get_db)):
    """
    (Admin Mock) Resets the usage counters for all users.
    This simulates a monthly cron job for testing plan limits.
    """
    try:
        num_rows_updated = db.query(models.UsageDB).update({
            models.UsageDB.words_scanned: 0,
            models.UsageDB.humanizer_uses: 0,
            models.UsageDB.last_reset: sa.func.now()
        })
        db.commit()
        print(f"ADMIN ACTION: Reset usage for {num_rows_updated} users.")
        return {"status": "success", "users_reset": num_rows_updated}
    except Exception as e:
        db.rollback()
        print(f"Error resetting all user usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not reset user usage."
        )
