from datetime import datetime
from dataclasses import dataclass


@dataclass
class PostDto:
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: str

    @classmethod
    def from_json(cls, json: dict):
        return cls(
            id=json["id"],
            title=json["title"],
            content=json["content"],
            created_at=datetime.fromisoformat(json["created_at"]),
            updated_at=datetime.fromisoformat(json["updated_at"]),
            user_id=json["user_id"],
        )
