"""
Основной класс клиента WATA API.
"""
import logging
from typing import Optional

from .http import AsyncHttpClient
from .modules import LinksModule, PaymentsModule, TransactionsModule, WebhooksModule

class WataClient:
    """Клиент для платежного API WATA."""

    def __init__(
        self,
        base_url: str,
        jwt_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        log_level: int = logging.INFO,
    ):
        """
        Инициализация клиента WATA API.

        Аргументы:
            base_url: Базовый URL API (продакшн или песочница)
            jwt_token: JWT-токен для аутентификации
            timeout: Таймаут запроса в секундах
            max_retries: Максимальное количество попыток повтора
            log_level: Уровень логирования
        """
        # Настройка логирования
        self.logger = logging.getLogger("wata_client")
        self.logger.setLevel(log_level)
        
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info(f"Инициализация клиента WATA с базовым URL: {base_url}")
        
        # Инициализация HTTP-клиента
        self.http = AsyncHttpClient(
            base_url=base_url,
            jwt_token=jwt_token,
            timeout=timeout,
            max_retries=max_retries,
        )
        
        # Инициализация модулей API
        self.links = LinksModule(self.http)
        self.payments = PaymentsModule(self.http)
        self.transactions = TransactionsModule(self.http)
        self.webhooks = WebhooksModule(self.http)

    async def close(self) -> None:
        """Закрыть HTTP-сессию."""
        await self.http.close()

    async def __aenter__(self):
        """Вход в контекстный менеджер."""
        self.logger.debug("Вход в контекстный менеджер")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера."""
        self.logger.debug("Выход из контекстного менеджера")
        await self.close()
