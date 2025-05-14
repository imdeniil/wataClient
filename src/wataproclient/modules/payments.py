"""
Модуль для работы с платежами.
"""
from typing import Any, Dict, Optional

from .base import BaseApiModule

class PaymentsModule(BaseApiModule):
    """Модуль для работы с платежами."""

    async def create_card_transaction(
        self,
        amount: float,
        currency: str,
        order_id: str,
        crypto: str,
        ip_address: str,
        browser_data: Dict[str, Any],
        description: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        notification_url: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Создание новой карточной транзакции.

        Аргументы:
            amount: Сумма платежа
            currency: Валюта платежа (RUB, EUR, USD)
            order_id: Идентификатор заказа в системе продавца
            crypto: Криптограмма, созданная скриптом checkout.js
            ip_address: IP-адрес плательщика
            browser_data: Данные браузера плательщика
            description: Описание платежа
            success_url: URL для перенаправления после успешного платежа
            fail_url: URL для перенаправления после неудачного платежа
            notification_url: URL веб-хука для уведомлений о платеже
            email: Email плательщика
            metadata: Дополнительные данные для включения в уведомления

        Возвращает:
            Детали транзакции

        Пример:
            ```python
            transaction = await client.payments.create_card_transaction(
                amount=100.50,
                currency="RUB",
                order_id="ORDER-123",
                crypto="YOUR_CRYPTOGRAM",
                ip_address="192.168.1.1",
                browser_data={
                    "colorDepth": 24,
                    "javaEnabled": False,
                    "language": "ru-RU",
                    "screenHeight": 1080,
                    "screenWidth": 1920,
                    "timezone": -180,
                    "userAgent": "Mozilla/5.0..."
                },
                description="Премиум-подписка"
            )
            ```
        """
        data = {
            "amount": amount,
            "currency": currency,
            "orderId": order_id,
            "crypto": crypto,
            "ipAddress": ip_address,
            "browserData": browser_data,
        }

        if description is not None:
            data["description"] = description
        if success_url is not None:
            data["successUrl"] = success_url
        if fail_url is not None:
            data["failUrl"] = fail_url
        if notification_url is not None:
            data["notificationUrl"] = notification_url
        if email is not None:
            data["email"] = email
        if metadata is not None:
            data["metadata"] = metadata

        self.logger.info(f"Создание карточной транзакции для заказа {order_id}")
        return await self.http.post("/payments/card-crypto", data=data)

    async def create_sbp_transaction(
        self,
        amount: float,
        currency: str,
        order_id: str,
        ip_address: str,
        browser_data: Dict[str, Any],
        description: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        notification_url: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Создание новой СБП транзакции.

        Аргументы:
            amount: Сумма платежа
            currency: Валюта платежа (RUB)
            order_id: Идентификатор заказа в системе продавца
            ip_address: IP-адрес плательщика
            browser_data: Данные браузера плательщика
            description: Описание платежа
            success_url: URL для перенаправления после успешного платежа
            fail_url: URL для перенаправления после неудачного платежа
            notification_url: URL веб-хука для уведомлений о платеже
            email: Email плательщика
            metadata: Дополнительные данные для включения в уведомления

        Возвращает:
            Детали транзакции с URL QR-кода

        Пример:
            ```python
            transaction = await client.payments.create_sbp_transaction(
                amount=100.50,
                currency="RUB",
                order_id="ORDER-123",
                ip_address="192.168.1.1",
                browser_data={
                    "colorDepth": 24,
                    "javaEnabled": False,
                    "language": "ru-RU",
                    "screenHeight": 1080,
                    "screenWidth": 1920,
                    "timezone": -180,
                    "userAgent": "Mozilla/5.0..."
                },
                description="Премиум-подписка"
            )
            qr_url = transaction["qrUrl"]
            ```
        """
        data = {
            "amount": amount,
            "currency": currency,
            "orderId": order_id,
            "ipAddress": ip_address,
            "browserData": browser_data,
        }

        if description is not None:
            data["description"] = description
        if success_url is not None:
            data["successUrl"] = success_url
        if fail_url is not None:
            data["failUrl"] = fail_url
        if notification_url is not None:
            data["notificationUrl"] = notification_url
        if email is not None:
            data["email"] = email
        if metadata is not None:
            data["metadata"] = metadata

        self.logger.info(f"Создание СБП транзакции для заказа {order_id}")
        return await self.http.post("/payments/sbp", data=data)

    async def get_public_key(self) -> Dict[str, Any]:
        """
        Получение публичного ключа для проверки подписи.

        Возвращает:
            Словарь, содержащий публичный ключ

        Пример:
            ```python
            public_key = await client.payments.get_public_key()
            key_value = public_key["key"]
            ```
        """
        self.logger.info("Получение публичного ключа")
        return await self.http.get("/public-key")
