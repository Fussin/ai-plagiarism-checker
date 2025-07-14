from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, checker, history, ai_tools, preview_api, admin_tools, subscription, users
from .config import settings
import os

# from .database import create_db_and_tables
# if settings.DEBUG: # Example: only create tables automatically in debug mode
#     print("DEBUG mode: Attempting to create database tables if they don't exist.")
#     create_db_and_tables()

app = FastAPI(title=settings.APP_NAME)

# Custom Exception Handler for structured errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Try to parse a more structured error code from the detail string if possible
    # e.g., if detail is "LIMIT_EXCEEDED: Monthly word limit exceeded."
    error_code = "GENERAL_ERROR"
    message = exc.detail
    if ":" in exc.detail:
        parts = exc.detail.split(":", 1)
        # A simple check to see if the first part is a valid-looking error code (e.g., UPPER_SNAKE_CASE)
        if parts[0].isupper() and " " not in parts[0]:
            error_code = parts[0]
            message = parts[1].strip()

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_code,
            "message": message,
        },
        headers=exc.headers,
    )


# CORS Middleware Configuration (origins updated for Next.js default)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(checker.router)
app.include_router(history.router)
app.include_router(ai_tools.router)
app.include_router(preview_api.router)
app.include_router(admin_tools.router)
app.include_router(subscription.router)
app.include_router(users.router) # Include the new users router

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} Backend"}
