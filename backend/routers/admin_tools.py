from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List

from backend import models
from backend.database import get_db
from backend.plans import PLAN_LIMITS

router = APIRouter(
    prefix="/admin",
    tags=["admin_tools"],
    # Note: In a real application, this entire router would be protected by
    # a dependency that checks if the current_user is an admin.
    # e.g., dependencies=[Depends(get_current_admin_user)]
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
