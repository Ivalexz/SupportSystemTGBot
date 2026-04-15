from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    CLIENT = "client"
    MANAGER = "manager"
    ADMIN = "admin"

class User(BaseModel):
    id: int
    username: str
    role: Role = Role.CLIENT
