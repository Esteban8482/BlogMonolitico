"""
Este archivo contiene la configuración de la base de datos.

- Configuración de la base de datos
- Modelos
    - User
    - Post
    - Comment
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
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # posts = db.relationship(
    #     "Post", backref="author", lazy=True, cascade="all, delete-orphan"
    # )
    comments = db.relationship(
        "Comment", backref="author", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
#     updated_at = db.Column(
#         db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
#     )
#     user_id = db.Column(
#         db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
#     )

#     comments = db.relationship(
#         "Comment", backref="post", lazy=True, cascade="all, delete-orphan"
#     )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    post_id = db.Column(db.Text, nullable=False)
