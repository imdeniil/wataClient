"""
Исключения для клиента WATA API.
"""
from typing import Any, Dict, Optional


class ApiError(Exception):
    """Базовое исключение для всех ошибок API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация ошибки API.

        Аргументы:
            message: Сообщение об ошибке
            status_code: HTTP-код состояния
            response_data: Исходные данные ответа
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Возвращает строковое представление ошибки."""
        if self.status_code:
            return f"{self.status_code} - {self.message}"
        return self.message


# Ошибки соединения
class ApiConnectionError(ApiError):
    """Ошибка подключения к API."""
    pass


class ApiTimeoutError(ApiConnectionError):
    """Тайм-аут запроса."""
    pass


# Ошибки аутентификации
class ApiAuthError(ApiError):
    """Ошибка аутентификации."""
    pass


class ApiForbiddenError(ApiError):
    """Доступ запрещен."""
    pass


# Ошибки ресурса
class ApiResourceNotFoundError(ApiError):
    """Запрашиваемый ресурс не найден."""
    pass


class ApiValidationError(ApiError):
    """Неверные параметры запроса."""
    pass


# Серверные ошибки
class ApiServerError(ApiError):
    """Ошибка сервера."""
    pass


class ApiServiceUnavailableError(ApiServerError):
    """Сервис временно недоступен."""
    pass


# Ошибки парсинга
class ApiParsingError(ApiError):
    """Ошибка парсинга ответа API."""
    pass


def create_api_error(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None,
) -> ApiError:
    """
    Создание соответствующей ошибки API на основе кода состояния.

    Аргументы:
        status_code: HTTP-код состояния
        message: Сообщение об ошибке
        response_data: Исходные данные ответа

    Возвращает:
        Экземпляр подкласса ApiError
    """
    if 400 <= status_code < 500:
        if status_code == 400:
            return ApiValidationError(message, status_code, response_data)
        elif status_code == 401:
            return ApiAuthError(message, status_code, response_data)
        elif status_code == 403:
            return ApiForbiddenError(message, status_code, response_data)
        elif status_code == 404:
            return ApiResourceNotFoundError(message, status_code, response_data)
        else:
            return ApiError(message, status_code, response_data)
    elif 500 <= status_code < 600:
        if status_code == 503:
            return ApiServiceUnavailableError(message, status_code, response_data)
        else:
            return ApiServerError(message, status_code, response_data)
    else:
        return ApiError(message, status_code, response_data)
