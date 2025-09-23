import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuración base de la app monolítica.

    - SECRET_KEY para sesiones
    - Ruta a credenciales de Firebase Admin para verificar tokens (Auth)
    """

    SECRET_KEY = (
        os.environ.get("USER_SECRET_KEY", secrets.token_hex(16)) or "super-secret-key"
    )

    # Credenciales del Admin SDK de Firebase (archivo JSON de cuenta de servicio)
    # Puede ser una ruta absoluta o relativa dentro del proyecto
    FIREBASE_ADMIN_CREDENTIALS = os.environ.get(
        "FIREBASE_ADMIN_CREDENTIALS",
        os.path.join(BASE_DIR, "firebase-admin.json"),
    )


class ServicesConfig:
    USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:5002")
    POST_SERVICE_URL = os.environ.get("POST_SERVICE_URL", "http://localhost:5003")
