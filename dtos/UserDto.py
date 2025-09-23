from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserDto:
<<<<<<< HEAD
    id: int
=======
    id: str  # Firebase UID
>>>>>>> main
    username: str
    bio: str
    created_at: datetime

    @classmethod
    def from_json(cls, json: dict):
        return cls(
<<<<<<< HEAD
            id=json["id"],
            username=json["username"],
            bio=json["bio"],
=======
            id=str(json["id"]),
            username=json["username"],
            bio=json.get("bio", ""),
>>>>>>> main
            created_at=datetime.fromisoformat(json["created_at"]),
        )
