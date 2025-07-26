from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import auth, checker, history, ai_tools, preview_api, admin_tools, subscription, users
from .config import settings
import os

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/hour"])
app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Exception Handler for structured errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_code = "GENERAL_ERROR"
    message = exc.detail
    if ":" in exc.detail:
        parts = exc.detail.split(":", 1)
        if parts[0].isupper() and " " not in parts[0]:
            error_code = parts[0]
            message = parts[1].strip()
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_code, "message": message},
        headers=exc.headers,
    )

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    # A basic Content Security Policy (CSP). This should be configured carefully for production.
    # It prevents loading resources from untrusted sources.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; " # 'unsafe-inline' might be needed for some libs, but is less secure
        "style-src 'self' 'unsafe-inline'; " # Same for styles
        "img-src 'self' data:; "
        "font-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self';"
    )
    return response

# CORS Middleware Configuration
# For production, you should restrict this to your specific frontend domain.
# Example: origins = ["https://your-frontend-domain.com"]
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

# Include all the application routers
app.include_router(auth.router)
app.include_router(checker.router)
app.include_router(history.router)
app.include_router(ai_tools.router)
app.include_router(preview_api.router)
app.include_router(admin_tools.router)
app.include_router(subscription.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} Backend"}
