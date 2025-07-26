from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text as DBText
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server_default=func.now()

from backend.database import Base # Import Base from database.py


# --- SQLAlchemy Models ---

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False) # New admin field
    plan = Column(String, default="free", nullable=False)
    subscription_status = Column(String, default="active", nullable=False)
    stripe_customer_id = Column(String, unique=True, index=True, nullable=True)

    scan_history = relationship("ScanHistoryDB", back_populates="owner")
    usage = relationship("UsageDB", back_populates="user", uselist=False) # one-to-one-ish (one per month, but simple for now)


class UsageDB(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True) # One usage record per user for simplicity
    # For monthly tracking, a composite key of (user_id, year_month) would be better.
    # Sticking to a simpler model for now as requested.
    # year_month = Column(String, nullable=False) # e.g., "2024-07"
    words_scanned = Column(Integer, default=0, nullable=False)
    humanizer_uses = Column(Integer, default=0, nullable=False)
    last_reset = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserDB", back_populates="usage")


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

class UsageSchema(BaseModel):
    words_scanned: int
    humanizer_uses: int
    last_reset: datetime

    class Config:
        from_attributes = True

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    plan: str
    subscription_status: str
    usage: Optional[UsageSchema] = None

    class Config:
        from_attributes = True

# Token Schemas (remain the same)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# Checker Request/Response Schemas
class TextCheckRequest(BaseModel): # Remains the same
    text: str

class PlagiarismResultSchema(BaseModel):
    originality_score: float
    matched_sources: List[str] = []
    rewrite_suggestions: List[str] = []
    can_download_report: bool = False # New field for plan enforcement

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
