from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime # Ensure datetime is imported

from .. import models # Pydantic models
from ..config import settings
# Corrected import for get_current_active_user
from ..dependencies import get_current_active_user, get_current_user

# For JWT
from jose import jwt # JWTError is not directly used here but good to know it exists
from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# In-memory user store (for demonstration purposes, replace with a database)
# Each user stored as: {"email": "user@example.com", "hashed_password": "...", "disabled": False}
fake_users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use ACCESS_TOKEN_EXPIRE_MINUTES from settings
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=models.Token)
async def signup(user_in: models.UserCreate): # Changed variable name for clarity
    if user_in.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user_in.password)
    # Storing user as a dictionary that matches parts of models.User
    fake_users_db[user_in.email] = {
        "email": user_in.email,
        "hashed_password": hashed_password,
        "disabled": False
        # Add other fields here if your models.User expects them and they have defaults or are Optional
    }

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username is used for the email field
    user_in_db = fake_users_db.get(form_data.username)
    if not user_in_db or not verify_password(form_data.password, user_in_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user_in_db.get("disabled"): # Check if user is disabled
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Example of a protected route using the dependency
@router.get("/users/me", response_model=models.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    # current_user is now the user dictionary from fake_users_db,
    # which Pydantic will validate against models.User
    # If get_current_active_user returns a Pydantic model instance, it's even cleaner.
    # For now, assuming it returns a dict that is compatible with models.User
    return current_user
