from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserReqDto:
    id: int
    username: str

    @classmethod
    def from_json(cls, json: dict):
        return cls(
            id=json["id"],
            username=json["username"],
        )
