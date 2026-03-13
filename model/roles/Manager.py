from typing import Optional
from pydantic import BaseModel

from User import RoleEnum

class Manager(BaseModel):
    user_id: int
    user_tg_id: str
    username: str
    role: RoleEnum = RoleEnum.manager

    @staticmethod
    def to_dict(user_id, user_tg_id, username, role=RoleEnum.manager) -> dict:
        return {
            "user_id": user_id,
            "user_tg_id": user_tg_id,
            "username": username,
            "role": role.value if isinstance(role, RoleEnum) else role,
        }
