from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from backend.main import limiter

from backend import models
from backend.config import settings
from backend.database import get_db
from backend.dependencies import get_current_active_user

from jose import jwt
from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

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
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> models.UserDB | None:
    return db.query(models.UserDB).filter(models.UserDB.email == email).first()

@router.post("/signup", response_model=models.Token)
@limiter.limit("10/minute") # Rate limit for signup
async def signup(request: Request, user_in: models.UserCreateSchema, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user_in.password)
    new_user = models.UserDB(email=user_in.email, hashed_password=hashed_password, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    initial_usage = models.UsageDB(user_id=new_user.id)
    db.add(initial_usage)
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=models.Token)
@limiter.limit("20/minute") # A slightly higher limit for login attempts
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_in_db = get_user_by_email(db, email=form_data.username)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user_in_db:
        print(f"Login attempt failed: User '{form_data.username}' not found.")
        raise credentials_exception

    if not verify_password(form_data.password, user_in_db.hashed_password):
        print(f"Login attempt failed: Incorrect password for user '{form_data.username}'.")
        raise credentials_exception

    if not user_in_db.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=models.UserSchema)
async def read_users_me(current_user: models.UserDB = Depends(get_current_active_user)):
    return current_user
