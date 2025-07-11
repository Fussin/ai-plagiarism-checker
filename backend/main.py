from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORS middleware
from .routers import auth, checker
from .config import settings
import os

app = FastAPI(title=settings.APP_NAME)

# Create upload and model directories (config.py also does this, defensive)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)

# CORS Middleware Configuration
# This allows the frontend (potentially on a different port like 8080 or when opening file directly)
# to communicate with the backend.
origins = [
    "http://localhost", # Common if frontend served by a simple server on default port
    "http://localhost:8080", # Common for Vite, React dev servers
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "null", # Allows opening index.html directly as a file in the browser (origin is "null")
    # Add any other origins if your frontend is hosted elsewhere during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allows cookies, authorization headers
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)

app.include_router(auth.router)
app.include_router(checker.router)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} Backend"}

# Further imports and global configurations can be added here
