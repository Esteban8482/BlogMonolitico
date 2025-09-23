from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserDto:
    id: str
    username: str
    bio: str
    created_at: datetime

    @classmethod
    def from_json(cls, json: dict):
        return cls(
            id=json["id"],
            username=json["username"],
            bio=json["bio"],
            created_at=datetime.fromisoformat(json["created_at"]),
        )
