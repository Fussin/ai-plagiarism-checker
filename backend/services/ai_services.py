from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from backend.config import settings

client = None
if settings.OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        client = None
else:
    print("OPENAI_API_KEY not found in settings. Text humanization feature will be disabled.")

async def humanize_text_with_gpt(text_to_humanize: str, model: str = "gpt-3.5-turbo") -> str | None:
    """
    Uses OpenAI's GPT model to "humanize" or rephrase the given text.
    Returns the humanized text or None if an error occurs or client is not available.
    """
    if not client:
        print("OpenAI client not initialized. Cannot humanize text.")
        return None

    if not text_to_humanize.strip():
        return text_to_humanize # Return original if empty or just whitespace

    try:
        # A simple prompt for rephrasing/humanizing.
        # This can be significantly improved with more sophisticated prompt engineering.
        prompt = (
            "Please rephrase the following text to make it sound more natural, engaging, and human-written. "
            "Focus on clarity, flow, and a conversational tone. Avoid overly complex vocabulary unless appropriate for the context. "
            "Do not add any prefatory remarks like 'Certainly, here's the rephrased text:'. Just provide the rephrased text directly.\n\n"
            "Original text:\n"
            f"\"\"\"{text_to_humanize}\"\"\"\n\n"
            "Rephrased text:"
        )

        completion = await client.chat.completions.create( # Use await for async client if available, or run sync in thread
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases text to sound more human and natural."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, # Controls randomness: lower for more deterministic, higher for more creative.
            max_tokens=len(text_to_humanize.split()) + 150, # Estimate based on input length + some buffer
            top_p=1.0,
            frequency_penalty=0.1, # Slightly penalize new token frequency
            presence_penalty=0.1   # Slightly penalize new token presence
        )

        humanized_text = completion.choices[0].message.content.strip()
        return humanized_text

    except APITimeoutError:
        print("OpenAI API request timed out.")
        return None
    except APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        return None
    except RateLimitError:
        print("OpenAI API request exceeded rate limit.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while calling OpenAI API: {e}")
        return None

# To run OpenAI's async client calls within FastAPI's synchronous routes without blocking,
# we should use `asyncio.to_thread` or ensure the client itself handles async correctly.
# OpenAI's client version >1.0.0 provides an AsyncOpenAI client.
# For simplicity here, if the above `await client.chat.completions.create` doesn't work directly
# in a synchronous FastAPI endpoint, it should be wrapped or a synchronous client call used.
# Let's assume for now the client supports await directly or we'll adjust in the router.

# Re-checking OpenAI library for async usage:
# The `OpenAI()` client is synchronous. For async, it should be `AsyncOpenAI()`.
# Let's adjust this service to be async-compatible for FastAPI.

from openai import AsyncOpenAI # Use AsyncOpenAI for FastAPI async routes

async_client = None
if settings.OPENAI_API_KEY:
    try:
        async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize AsyncOpenAI client: {e}")
        async_client = None
else:
    # This message is already printed above, but good to have context here too.
    print("OPENAI_API_KEY not found for AsyncOpenAI client.")


async def humanize_text_with_gpt_async(text_to_humanize: str, model: str = "gpt-3.5-turbo") -> str | None:
    if not async_client:
        print("AsyncOpenAI client not initialized. Cannot humanize text.")
        # Could raise an HTTPException here to inform the client properly
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Text humanization service is not available.")

    if not text_to_humanize.strip():
        return text_to_humanize

    prompt = (
        "Please rephrase the following text to make it sound more natural, engaging, and human-written. "
        "Focus on clarity, flow, and a conversational tone. Avoid overly complex vocabulary unless appropriate for the context. "
        "Do not add any prefatory remarks like 'Certainly, here's the rephrased text:'. Just provide the rephrased text directly.\n\n"
        "Original text:\n"
        f"\"\"\"{text_to_humanize}\"\"\"\n\n"
        "Rephrased text:"
    )

    try:
        completion = await async_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases text to sound more human and natural."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            # Estimate max_tokens carefully. If input is long, this needs to be larger.
            # OpenAI charges based on input and output tokens.
            max_tokens=int(len(text_to_humanize.split()) * 1.5) + 50, # Heuristic: 1.5x words + 50
            top_p=1.0,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        humanized_text = completion.choices[0].message.content.strip()
        return humanized_text
    except APITimeoutError:
        print("OpenAI API request timed out.")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="OpenAI API request timed out.")
    except APIError as e: # Catch more specific API errors if possible
        print(f"OpenAI API returned an API Error: {e.body}") # e.body might have more details
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"OpenAI API error: {e.message}")
    except RateLimitError:
        print("OpenAI API request exceeded rate limit.")
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded with OpenAI API.")
    except Exception as e:
        print(f"An unexpected error occurred while calling OpenAI API: {e}")
        # Consider logging the full traceback for unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error during text humanization.")

# For FastAPI's status codes
from fastapi import HTTPException, status
