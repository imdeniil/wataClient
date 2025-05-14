"""
Асинхронный HTTP-клиент для WATA API.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import aiohttp

from .exceptions import (
    ApiConnectionError,
    ApiError,
    ApiParsingError,
    ApiTimeoutError,
    create_api_error,
)


class AsyncHttpClient:
    """Асинхронный HTTP-клиент для WATA API."""

    def __init__(
        self,
        base_url: str,
        jwt_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_statuses: Optional[List[int]] = None,
        retry_backoff_factor: float = 0.5,
    ):
        """
        Инициализация HTTP-клиента.

        Аргументы:
            base_url: Базовый URL API
            jwt_token: JWT-токен для аутентификации
            timeout: Таймаут запроса в секундах
            max_retries: Максимальное количество попыток повтора
            retry_statuses: HTTP-коды состояния, которые должны вызывать повторную попытку
            retry_backoff_factor: Фактор задержки для повторных попыток
        """
        self.base_url = base_url
        self.jwt_token = jwt_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_statuses = retry_statuses or [502, 503, 504]
        self.retry_backoff_factor = retry_backoff_factor
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получить или создать экземпляр aiohttp ClientSession.

        Возвращает:
            Экземпляр aiohttp.ClientSession
        """
        async with self.session_lock:
            if self.session is None or self.session.closed:
                self.logger.debug("Создание новой HTTP-сессии")
                self.session = aiohttp.ClientSession()
            return self.session

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Получить заголовки запроса с JWT-токеном, если он предоставлен.

        Аргументы:
            additional_headers: Дополнительные заголовки для включения

        Возвращает:
            Словарь HTTP-заголовков
        """
        headers = {"Content-Type": "application/json"}
        
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
            
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    def _build_url(self, endpoint: str) -> str:
        """
        Построить полный URL для указанной конечной точки.

        Аргументы:
            endpoint: Путь к конечной точке API

        Возвращает:
            Полный URL
        """
        # Убедимся, что endpoint начинается со слеша, если его еще нет
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
            
        return urljoin(self.base_url, endpoint)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP-запрос с автоматическими повторными попытками для определенных кодов состояния.

        Аргументы:
            method: HTTP-метод (GET, POST и т.д.)
            endpoint: Конечная точка API для вызова
            params: Параметры URL
            data: Тело запроса
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа

        Вызывает:
            ApiError: Если запрос не удался
        """
        url = self._build_url(endpoint)
        all_headers = self._get_headers(headers)
        session = await self._get_session()
        json_data = None if data is None else json.dumps(data)

        self.logger.debug(f"Запрос: {method} {url}")
        if params:
            self.logger.debug(f"Параметры: {params}")
        if data:
            self.logger.debug(f"Данные: {data}")

        retry_count = 0
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        while True:
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    data=json_data,
                    headers=all_headers,
                    timeout=timeout,
                ) as response:
                    response_text = await response.text()
                    
                    self.logger.debug(f"Статус ответа: {response.status}")
                    self.logger.debug(f"Тело ответа: {response_text}")

                    # Попытка разобрать ответ как JSON
                    response_data = {}
                    if response_text:
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            if response.status >= 400:
                                raise ApiParsingError(
                                    f"Не удалось разобрать ответ с ошибкой: {response_text}",
                                    response.status,
                                )
                            response_data = {"content": response_text}

                    # Проверка успешного ответа
                    if 200 <= response.status < 300:
                        return response_data

                    # Обработка неудачных запросов
                    error_message = response_data.get("message", str(response_data)) if isinstance(response_data, dict) else str(response_data)
                    if not error_message:
                        error_message = f"Запрос не удался с кодом состояния {response.status}"

                    # Проверка, следует ли повторить
                    if response.status in self.retry_statuses and retry_count < self.max_retries:
                        retry_count += 1
                        wait_time = self.retry_backoff_factor * (2 ** (retry_count - 1))
                        self.logger.warning(
                            f"Запрос не удался со статусом {response.status}. "
                            f"Повторная попытка через {wait_time:.2f}с ({retry_count}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    # Нет больше повторных попыток, вызываем ошибку
                    raise create_api_error(response.status, error_message, response_data)

            except aiohttp.ClientError as e:
                # Обработка ошибок соединения
                if isinstance(e, aiohttp.ClientConnectorError):
                    error_message = f"Ошибка соединения: {str(e)}"
                    error = ApiConnectionError(error_message)
                elif isinstance(e, asyncio.TimeoutError):
                    error_message = f"Тайм-аут запроса после {self.timeout}с"
                    error = ApiTimeoutError(error_message)
                else:
                    error_message = f"Сбой запроса: {str(e)}"
                    error = ApiConnectionError(error_message)

                # Проверка, следует ли повторить
                if retry_count < self.max_retries:
                    retry_count += 1
                    wait_time = self.retry_backoff_factor * (2 ** (retry_count - 1))
                    self.logger.warning(
                        f"{error_message}. "
                        f"Повторная попытка через {wait_time:.2f}с ({retry_count}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue

                # Нет больше повторных попыток, вызываем ошибку
                self.logger.error(f"{error_message}. Достигнуто максимальное количество повторных попыток.")
                raise error

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить GET-запрос.

        Аргументы:
            endpoint: Конечная точка API для вызова
            params: Параметры URL
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа
        """
        return await self._request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить POST-запрос.

        Аргументы:
            endpoint: Конечная точка API для вызова
            data: Тело запроса
            params: Параметры URL
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа
        """
        return await self._request("POST", endpoint, params=params, data=data, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить PUT-запрос.

        Аргументы:
            endpoint: Конечная точка API для вызова
            data: Тело запроса
            params: Параметры URL
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа
        """
        return await self._request("PUT", endpoint, params=params, data=data, headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить PATCH-запрос.

        Аргументы:
            endpoint: Конечная точка API для вызова
            data: Тело запроса
            params: Параметры URL
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа
        """
        return await self._request("PATCH", endpoint, params=params, data=data, headers=headers)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить DELETE-запрос.

        Аргументы:
            endpoint: Конечная точка API для вызова
            params: Параметры URL
            headers: Дополнительные заголовки

        Возвращает:
            Разобранные данные ответа
        """
        return await self._request("DELETE", endpoint, params=params, headers=headers)

    async def close(self) -> None:
        """Закрыть HTTP-сессию."""
        if self.session and not self.session.closed:
            self.logger.debug("Закрытие HTTP-сессии")
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        """Вход в асинхронный контекстный менеджер."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из асинхронного контекстного менеджера."""
        await self.close()
