"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- Modelos
    - User para nombre y datos personales como biografía
"""

from datetime import datetime
from dataclasses import dataclass


# =============================
# MODELOS
# =============================
@dataclass
class User:
    """
    No es un modelo soportado por Firestore.
    Sin embargo nos ayuda a modelar la información de un usuario, sin tener que usar JSON manualmente por cada operación.
    """

    id: str | None = None
    username: str = ""
    bio: str = ""
    created_at: datetime = datetime.now()

    def __repr__(self):
        return f"<User {self.username} {self.id=} {self.created_at=} {self.bio=}>"

    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "bio": self.bio,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_json(cls, json: dict):
        if json is None:
            return None

        return cls(
            id=json["id"],
            username=json["username"],
            bio=json["bio"],
            created_at=datetime.fromisoformat(json["created_at"]),
        )
