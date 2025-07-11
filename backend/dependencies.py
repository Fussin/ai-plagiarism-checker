from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import TokenData, UserDB # UserDB is the SQLAlchemy model
from backend.database import get_db # Database session dependency
from backend.routers.auth import get_user_by_email # Helper to query user by email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=token_data.email) # Fetch user from DB
    if user is None:
        raise credentials_exception
    return user # Returns UserDB instance

async def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_active: # Check the 'is_active' field from UserDB model
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
