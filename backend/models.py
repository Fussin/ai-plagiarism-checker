from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text as DBText
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server_default=func.now()

from backend.database import Base # Import Base from database.py


# --- SQLAlchemy Models ---

class UserDB(Base): # Renamed to UserDB to distinguish from Pydantic User schema
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    # Add any other fields like created_at, updated_at
    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to ScanHistory (one-to-many)
    scan_history = relationship("ScanHistoryDB", back_populates="owner")


class ScanHistoryDB(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    content_type = Column(String, nullable=False) # e.g., "text", "file_pdf", "image_jpeg", "video_mp4"
    file_name = Column(String, nullable=True) # Original filename if applicable
    input_snippet = Column(DBText, nullable=True) # A short snippet of text or description
    originality_score = Column(Float, nullable=False)
    # Storing complex objects like lists/dicts as JSON strings or in a related table.
    # For simplicity, using Text and handling JSON manually or via TypeDecorator later if needed.
    matched_sources_json = Column(DBText, nullable=True) # JSON string of list
    rewrite_suggestions_json = Column(DBText, nullable=True) # JSON string of list

    owner = relationship("UserDB", back_populates="scan_history")


# --- Pydantic Schemas (for API validation and response) ---

# User Schemas
class UserBaseSchema(BaseModel): # Changed suffix to Schema
    email: EmailStr

class UserCreateSchema(UserBaseSchema):
    password: str

class UserLoginSchema(UserBaseSchema):
    password: str

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    # scan_history: List['ScanHistorySchema'] = [] # Avoid circular dependency if ScanHistorySchema defined later

    class Config:
        from_attributes = True # Pydantic v2 (formerly orm_mode)

# Token Schemas (remain the same)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# Checker Request/Response Schemas
class TextCheckRequest(BaseModel): # Remains the same
    text: str

class PlagiarismResultSchema(BaseModel): # Changed suffix to Schema
    originality_score: float
    matched_sources: List[str] = []
    rewrite_suggestions: List[str] = []

    class Config:
        from_attributes = True

# ScanHistory Schemas
class ScanHistoryBaseSchema(BaseModel):
    content_type: str
    file_name: Optional[str] = None
    input_snippet: Optional[str] = None
    originality_score: float
    matched_sources: List[str] = []
    rewrite_suggestions: List[str] = []

class ScanHistoryCreateSchema(ScanHistoryBaseSchema):
    pass # user_id will be set from current_user in endpoint

class ScanHistorySchema(ScanHistoryBaseSchema):
    id: int
    user_id: int
    timestamp: datetime # Import datetime from typing or use pydantic's datetime

    class Config:
        from_attributes = True

# Need to import datetime for ScanHistorySchema
from datetime import datetime

# Update UserSchema to include ScanHistory if needed, carefully handling potential circular imports
# UserSchema.model_rebuild() # For Pydantic v2

# --- AI Tools Schemas ---

class TextHumanizationRequest(BaseModel):
    text: str
    model: Optional[str] = "gpt-4-turbo" # Defaulting to a GPT-4 class model

class TextHumanizationResponse(BaseModel):
    original_text: str
    humanized_text: str | None
    model_used: str
    error: Optional[str] = None

# --- Preview API Schemas ---

class FilePreviewItem(BaseModel):
    filename: str
    content_type: str
    preview: Optional[str] = None # First 500 chars for text, or type message
    error: Optional[str] = None

class FilePreviewResponse(BaseModel):
    results: List[FilePreviewItem]
