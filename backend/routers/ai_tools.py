from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from backend import models # Pydantic schemas
from backend.services.ai_services import humanize_text_with_gpt_async # The async version
from backend.dependencies import get_current_active_user # Optional: make this a protected endpoint

router = APIRouter(
    prefix="/ai",
    tags=["ai_tools"],
    # dependencies=[Depends(get_current_active_user)] # Uncomment if this should be a protected feature
)

@router.post("/humanize-text", response_model=models.TextHumanizationResponse)
async def humanize_text_endpoint(
    request: models.TextHumanizationRequest,
    # current_user: models.UserDB = Depends(get_current_active_user) # Uncomment if protected
):
    """
    Receives text and returns a "humanized" version using an LLM.
    """
    if not request.text.strip():
        return models.TextHumanizationResponse(
            original_text=request.text,
            humanized_text=request.text, # Return original if empty
            model_used=request.model,
            error="Input text was empty."
        )

    try:
        humanized_text = await humanize_text_with_gpt_async(request.text, model=request.model)

        if humanized_text is None:
            # The service function now raises HTTPExceptions for specific API errors,
            # so this part might only be reached for very generic None returns not covered by those.
            # However, it's good practice to handle it.
             return models.TextHumanizationResponse(
                original_text=request.text,
                humanized_text=None,
                model_used=request.model,
                error="Failed to humanize text. Service returned no content."
            )

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
