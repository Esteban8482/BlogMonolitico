"""
Auth Service (deprecated for SQL/local auth).

La autenticación ahora es manejada por Firebase Authentication (lado cliente)
y verificada en el servidor mediante el Admin SDK. Este módulo queda como
fachada mínima para evitar imports rotos, pero no debe usarse para crear o
validar usuarios mediante base de datos local.
"""

from typing import Optional
from db_connector import User


def register_user(*args, **kwargs) -> Optional[User]:
    """Registro de usuario debe realizarse en Firebase. Retorna None."""
    return None


def authenticate_user(*args, **kwargs) -> Optional[User]:
    """La autenticación se hace via Firebase. Retorna None."""
    return None


def get_user_by_id(*args, **kwargs) -> Optional[User]:
    """Sin base de datos local, no se puede resolver por ID. Retorna None."""
    return None
