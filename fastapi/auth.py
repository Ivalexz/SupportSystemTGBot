from fastapi import HTTPException

ALLOWED_ROLES = {'Client', 'Manager', 'Admin'}


def validate_role(role: str) -> str:
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail='Invalid role')
    return role


def require_staff(role: str) -> str:
    validate_role(role)
    if role not in {'Manager', 'Admin'}:
        raise HTTPException(status_code=403, detail='Access denied')
    return role


def require_admin(role: str) -> str:
    validate_role(role)
    if role != 'Admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    return role
