from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend import models
from backend.database import get_db
from backend.services import ai_services, usage_service, text_processing
from backend.dependencies import get_current_active_user

router = APIRouter(
    prefix="/ai",
    tags=["ai_tools"],
    dependencies=[Depends(get_current_active_user)] # This is now a protected feature
)

@router.post("/humanize-text", response_model=models.TextHumanizationResponse)
async def humanize_text_endpoint(
    request: models.TextHumanizationRequest,
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(get_current_active_user)
):
    """
    Receives text and returns a "humanized" version using an LLM,
    respecting the user's plan limits.
    """
    usage = usage_service.get_or_create_usage_record(db, current_user)
    word_count = text_processing.count_words(request.text)

    if word_count == 0:
        return models.TextHumanizationResponse(
            original_text=request.text,
            humanized_text=request.text,
            model_used=request.model,
            error="Input text was empty."
        )

    # Check if user has enough quota for this action
    if not usage_service.check_humanizer_limit(current_user, usage, word_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have exceeded your monthly limit for the text humanizer. Please upgrade your plan."
        )

    try:
        humanized_text = await humanize_text_with_gpt_async(request.text, model=request.model)

        if humanized_text is None:
            # The service function now raises HTTPExceptions for specific API errors,
            # so this part might only be reached for very generic None returns not covered by those.
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to humanize text. Service returned no content.")

        # If successful, update usage
        usage_service.update_usage(db, usage, humanizer_uses=word_count)

        return models.TextHumanizationResponse(
            original_text=request.text,
            humanized_text=humanized_text,
            model_used=request.model
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions raised by the service layer (like 503, 504, 429)
        # Or handle them to return a consistent response model format
        return models.TextHumanizationResponse(
            original_text=request.text,
            humanized_text=None,
            model_used=request.model,
            error=f"Service Error: {e.detail}" # Or e.status_code for more context
        )
    except Exception as e:
        # Catch any other unexpected errors from the service call not already an HTTPException
        print(f"Unexpected error in humanize_text_endpoint: {e}") # Log this
        return models.TextHumanizationResponse(
            original_text=request.text,
            humanized_text=None,
            model_used=request.model,
            error="An unexpected internal error occurred during text humanization."
        )

# Example of how to protect it:
# @router.post("/humanize-text-protected", response_model=models.TextHumanizationResponse)
# async def humanize_text_protected_endpoint(
#     request: models.TextHumanizationRequest,
#     current_user: models.UserDB = Depends(get_current_active_user)
# ):
#    # ... same logic as above ...
#    # The current_user dependency ensures only authenticated users can access.
#    pass
