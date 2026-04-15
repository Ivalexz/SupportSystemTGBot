from pydantic import BaseModel
from datetime import datetime


class Comment(BaseModel):
    comment_id: int
    request_id: int
    user_id: int
    text: str
    created_at: datetime = datetime.utcnow()

    @staticmethod
    def to_dict(comment_id, request_id, user_id, text, created_at=None) -> dict:
        return {
            "comment_id": comment_id,
            "request_id": request_id,
            "user_id": user_id,
            "text": text,
            "created_at": created_at or datetime.utcnow(),
        }



