from fastapi import HTTPException
from fastapi import Depends, status
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

ALLOWED_ROLES = {'client', 'manager', 'admin'}
security_key = "some_key123"
algorithm = "HS256"
access_token_time_min = 60
auth_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(telegram_id: int, role: str) -> str:
    access_token_expires = datetime.now() + timedelta(minutes=access_token_time_min)

    jwt_payload = {"telegram_id": telegram_id, "role": role, "exp": access_token_expires}
    return jwt.encode(jwt_payload, security_key, algorithm=algorithm)

def get_current_user(token: str = Depends(auth_scheme)):
    try:
        payload = jwt.decode(token, security_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def get_current_manager(current_user: Dict = Depends(get_current_user)):
    if current_user.get("role") not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")
    return current_user

def get_current_admin(current_user: Dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user




def validate_role(role: str) -> str:
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail='Invalid role')
    return role


def require_staff(role: str) -> str:
    validate_role(role)
    if role not in {'manager', 'admin'}:
        raise HTTPException(status_code=403, detail='Access denied')
    return role


def require_admin(role: str) -> str:
    validate_role(role)
    if role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    return role
