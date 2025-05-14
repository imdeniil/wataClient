"""
Клиент платежного API WATA.

Модульный асинхронный клиент для взаимодействия с платежным API WATA.
"""

from .client import WataClient
from .manager import WataClientManager
from .exceptions import (
    ApiAuthError,
    ApiConnectionError,
    ApiError,
    ApiForbiddenError,
    ApiParsingError,
    ApiResourceNotFoundError,
    ApiServerError,
    ApiServiceUnavailableError,
    ApiTimeoutError,
    ApiValidationError,
)

__all__ = [
    "WataClient",
    "WataClientManager",
    "ApiError",
    "ApiConnectionError",
    "ApiTimeoutError",
    "ApiAuthError",
    "ApiForbiddenError",
    "ApiResourceNotFoundError",
    "ApiValidationError",
    "ApiServerError",
    "ApiServiceUnavailableError",
    "ApiParsingError",
]

__version__ = "1.0.0"
