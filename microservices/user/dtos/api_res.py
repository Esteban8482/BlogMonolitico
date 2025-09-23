from flask import jsonify
from typing import TypeVar, Generic, Optional, Union
from log import logger

T = TypeVar("T")


class ApiRes(Generic[T]):
    """
    Clase que representa una respuesta de la API

    - success: bool true -> http status 200 al 299
    - message: str
    - data: T -> cualquier objeto o tipo
    - error: bool -> http status 500 al 599
    """

    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[T],
        status_code: int = 200,
        error: bool = False,
    ):
        self.success = success
        self.message = message
        self.data = data
        self.status_code = status_code
        self.error = error

        if success:
            logger.info(message)
        else:
            logger.error(message)

    def to_json(self):
        try:
            data_json = (
                self.data.to_json() if hasattr(self.data, "to_json") else self.data
            )
        except Exception:
            data_json = self.data

        return {
            "success": self.success,
            "message": self.message,
            "data": data_json,
        }

    def flask_response(self):
        return jsonify(self.to_json()), self.status_code

    def __repr__(self):
        return f"<ApiRes {self.success} {self.message} {self.data}>"

    def __str__(self):
        return f"<ApiRes {self.success} {self.message} {self.data}>"

    def __bool__(self):
        return self.success

    @staticmethod
    def success(message: str = "Success", data: Optional[T] = None) -> "ApiRes[T]":
        return ApiRes(True, message, data, 200)

    @staticmethod
    def created(message: str = "Creado", data: Optional[T] = None) -> "ApiRes[T]":
        return ApiRes(True, message, data, 201)

    @staticmethod
    def internal_error(
        message: str = "Error Interno", status_code: int = 500, data: Optional[T] = None
    ) -> "ApiRes[T]":
        return ApiRes(False, message, data, status_code, True)

    @staticmethod
    def error(
        message: str = "Error", data: Optional[T] = None, status_code: int = 400
    ) -> "ApiRes[T]":
        return ApiRes(False, message, data, status_code)

    @staticmethod
    def not_found(message: str = "Not found", data: Optional[T] = None) -> "ApiRes[T]":
        return ApiRes(False, message, data, 404)

    @staticmethod
    def unauthorized(
        message: str = "No autorizado", data: Optional[T] = None
    ) -> "ApiRes[T]":
        return ApiRes(False, message, data, 401)

    @staticmethod
    def forbidden(
        message: str = "Prohibido, no autorizado", data: Optional[T] = None
    ) -> "ApiRes[T]":
        return ApiRes(False, message, data, 403)

    @staticmethod
    def conflict(message: str = "Conflicto", data: Optional[T] = None) -> "ApiRes[T]":
        return ApiRes(False, message, data, 409)
