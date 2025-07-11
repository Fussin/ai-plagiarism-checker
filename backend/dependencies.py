from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .config import settings
from .models import TokenData
# Assuming fake_users_db is accessible for user lookup, or we adapt.
# For now, we'll just validate the token and extract email.
# A more robust solution would fetch user details from the DB.
from .routers.auth import fake_users_db # Temporary for user validation

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Matches the login route

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(email) # Check if user exists in our mock DB
    if user is None:
        raise credentials_exception
    if user.get("disabled"): # Check if user is marked as disabled
         raise HTTPException(status_code=400, detail="Inactive user")

    return user # Return the user dict from fake_users_db (or a user model instance)

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    # This is a convenience dependency if you want to ensure the user is active
    # The check for "disabled" is already in get_current_user for this basic setup.
    # If get_current_user only returned TokenData, this would be more distinct.
    if current_user.get("disabled"): # Redundant if get_current_user already checks
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
