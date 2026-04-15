from pydantic import BaseModel
from datetime import datetime


class Msg(BaseModel):
    msg_id: int
    user_tg_id: str
    text: str
    created_at: datetime = datetime.utcnow()

    @staticmethod
    def to_dict(msg_id, user_tg_id, text, created_at=None) -> dict:
        return {
            "msg_id": msg_id,
            "user_tg_id": user_tg_id,
            "text": text,
            "created_at": created_at or datetime.utcnow(),
        }