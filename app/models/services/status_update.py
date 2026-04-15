from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class RequestStatus(str, Enum):
    New = "New"
    In_Progress = "In Progress"
    Done = "Done"

class StatusUpdate(BaseModel):
    id: int
    request_id: int
    user_id: int
    new_status: RequestStatus
    updated_at: datetime = datetime.now()