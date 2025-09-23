"""
Este archivo antes contenía la configuración de SQLAlchemy y modelos locales.
Como parte de la migración a Firebase, ya no usamos una base de datos local
para autenticación. Mantendremos una representación mínima de usuario para la sesión.
"""

from dataclasses import dataclass


@dataclass
class User:
    id: str
    username: str
    email: str | None = None
