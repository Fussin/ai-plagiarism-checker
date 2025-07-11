from pydantic import BaseModel, EmailStr
from typing import Optional, List # Ensure List is imported

# --- User and Auth Models ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    disabled: Optional[bool] = None
    class Config:
        from_attributes = True # Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None


# --- Checker Request/Response Models ---
class TextCheckRequest(BaseModel):
    text: str

class PlagiarismResult(BaseModel):
    originality_score: float
    matched_sources: List[str] = []
    rewrite_suggestions: List[str] = [] # New field for suggestions

# Add other models as needed
