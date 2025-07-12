from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, checker, history, ai_tools, preview_api, admin_tools # Import admin_tools
from .config import settings
import os

# from .database import create_db_and_tables
# if settings.DEBUG: # Example: only create tables automatically in debug mode
#     print("DEBUG mode: Attempting to create database tables if they don't exist.")
#     create_db_and_tables()

app = FastAPI(title=settings.APP_NAME)

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
app.include_router(admin_tools.router) # Include the new admin_tools router

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} Backend"}
