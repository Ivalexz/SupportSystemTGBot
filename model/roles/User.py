from pydantic import BaseModel
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(BaseModel):
    user_id: int
    user_tg_id: str
    username: str
    role: RoleEnum = RoleEnum.user

    @staticmethod
    def to_dict(user_id, user_tg_id, username, role) -> dict:
        return {
            "user_id": user_id,
            "user_tg_id": user_tg_id,
            "username": username,
            "role": role.value if isinstance(role, RoleEnum) else role,
        }


