"""
Este archivo contiene la configuración de la base de datos.

- Configuración de la base de datos
- Modelos
    - User para nombre y datos personales como biografía
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# =============================
# MODELOS
# =============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username} {self.id=} {self.created_at=} {self.bio=}>"

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_json(cls, json: dict):
        return cls(
            id=json["id"],
            username=json["username"],
            bio=json["bio"],
            created_at=datetime.fromisoformat(json["created_at"]),
        )
