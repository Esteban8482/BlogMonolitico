"""
Este archivo contiene la configuración de la base de datos y modelos en Firestore.

- Configuración de la base de datos
- Modelos
    - Post para contenido de una publicación
"""

from datetime import datetime
from dataclasses import dataclass


# =============================
# MODELOS
# =============================
@dataclass
class Post:
    """
    No es un modelo soportado por Firestore.
    Sin embargo nos ayuda a modelar la información de un post, sin tener que usar JSON manualmente por cada operación.
    """

    id: str | None = None
    title: str = ""
    content: str = ""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    user_id: str = ""
    # redundancia de datos pero permite no hacer llamadas a la API de usuario
    username: str = ""

    def __repr__(self):
        return f"<Post {self.title} {self.id=} {self.created_at=} {self.content=} {self.user_id=}>"

    def to_json(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
            "username": self.username,
        }

    @classmethod
    def from_json(cls, json: dict):
        if json is None:
            return None

        return cls(
            id=json["id"],
            title=json["title"],
            content=json["content"],
            created_at=datetime.fromisoformat(json["created_at"]),
            updated_at=datetime.fromisoformat(json["updated_at"]),
            user_id=json["user_id"],
            username=json["username"],
        )
