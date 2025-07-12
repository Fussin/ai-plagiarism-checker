from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.models import UserDB, UsageDB
from backend.plans import get_plan_limits

def get_or_create_usage_record(db: Session, user: UserDB) -> UsageDB:
    """
    Retrieves a user's usage record. If it doesn't exist, creates one.
    Also handles resetting the usage if a new month has started.
    """
    usage_record = db.query(UsageDB).filter(UsageDB.user_id == user.id).first()

    # If no record exists, create one
    if not usage_record:
        usage_record = UsageDB(user_id=user.id)
        db.add(usage_record)
        db.commit()
        db.refresh(usage_record)
        return usage_record

    # Check if the usage needs to be reset (new month)
    now = datetime.now(timezone.utc)
    if usage_record.last_reset.year != now.year or usage_record.last_reset.month != now.month:
        print(f"Resetting usage for user {user.email} for new month {now.strftime('%Y-%m')}.")
        usage_record.words_scanned = 0
        usage_record.humanizer_uses = 0
        usage_record.last_reset = now
        db.commit()
        db.refresh(usage_record)

    return usage_record

def check_word_limit(user: UserDB, usage: UsageDB, new_words: int) -> bool:
    """
    Checks if scanning new_words will exceed the user's monthly word limit.
    Returns True if within limit, False otherwise.
    """
    plan_limits = get_plan_limits(user.plan)
    if usage.words_scanned + new_words > plan_limits["monthly_word_limit"]:
        return False
    return True

def check_humanizer_limit(user: UserDB, usage: UsageDB, new_words: int) -> bool:
    """
    Checks if using the humanizer for new_words will exceed the allowed usage.
    Returns True if within limit, False otherwise.
    """
    plan_limits = get_plan_limits(user.plan)
    humanizer_allowance = plan_limits["monthly_word_limit"] * plan_limits["humanizer_usage_percent"]

    if usage.humanizer_uses + new_words > humanizer_allowance:
        return False
    return True

def update_usage(db: Session, usage: UsageDB, words_scanned: int = 0, humanizer_uses: int = 0):
    """
    Updates the usage record with new scanned words or humanizer uses.
    """
    usage.words_scanned += words_scanned
    usage.humanizer_uses += humanizer_uses
    db.commit()
    db.refresh(usage)
    print(f"Updated usage for user_id {usage.user_id}: words={usage.words_scanned}, humanizer={usage.humanizer_uses}")
