from pydantic import BaseModel
from datetime import datetime


class TicketRequest(BaseModel):
    telegram_id: int
    title: str
    description: str
    created_at: datetime = datetime.utcnow()

    @staticmethod
    def to_dict(telegram_id, title, description, created_at=None) -> dict:
        return {
            "telegram_id": telegram_id,
            "title": title,
            "description": description,
            "created_at": created_at or datetime.utcnow()
        }