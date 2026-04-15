from pydantic import BaseModel
from datetime import datetime
from .status_update import RequestStatus


class TicketRequest(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: RequestStatus = RequestStatus.New
    created_at: datetime = datetime.now()

