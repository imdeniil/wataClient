"""
Модуль для работы с платежными ссылками.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .base import BaseApiModule


class LinksModule(BaseApiModule):
    """Модуль для работы с платежными ссылками."""

    async def create(
        self,
        amount: float,
        currency: str,
        order_id: str,
        description: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        notification_url: Optional[str] = None,
        lifetime_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        payer_account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Создание новой платежной ссылки.

        Аргументы:
            amount: Сумма платежа (может иметь до 2 десятичных знаков)
            currency: Валюта платежа (RUB, EUR, USD)
            order_id: Идентификатор заказа в системе продавца
            description: Описание платежа
            success_url: URL для перенаправления после успешного платежа
            fail_url: URL для перенаправления после неудачного платежа
            notification_url: URL веб-хука для уведомлений о платеже
            lifetime_seconds: Время жизни ссылки в секундах
            metadata: Дополнительные данные для включения в уведомления
            payer_account: Идентификатор аккаунта плательщика

        Возвращает:
            Детали платежной ссылки, включая URL

        Пример:
            ```python
            link = await client.links.create(
                amount=100.50,
                currency="RUB",
                order_id="ORDER-123",
                description="Премиум-подписка",
                success_url="https://example.com/success",
                fail_url="https://example.com/fail"
            )
            payment_url = link["url"]
            ```
        """
        data = {
            "amount": amount,
            "currency": currency,
            "orderId": order_id,
        }

        if description is not None:
            data["description"] = description
        if success_url is not None:
            data["successUrl"] = success_url
        if fail_url is not None:
            data["failUrl"] = fail_url
        if notification_url is not None:
            data["notificationUrl"] = notification_url
        if lifetime_seconds is not None:
            data["lifetimeSeconds"] = lifetime_seconds
        if metadata is not None:
            data["metadata"] = metadata
        if payer_account is not None:
            data["payerAccount"] = payer_account

        self.logger.info(f"Создание платежной ссылки для заказа {order_id}")
        return await self.http.post("/links", data=data)

    async def get(self, link_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Получение деталей платежной ссылки по ID.

        Аргументы:
            link_id: UUID платежной ссылки

        Возвращает:
            Детали платежной ссылки

        Пример:
            ```python
            link = await client.links.get("550e8400-e29b-41d4-a716-446655440000")
            print(f"Статус ссылки: {link['status']}")
            ```
        """
        link_id_str = str(link_id)
        self.logger.info(f"Получение платежной ссылки {link_id_str}")
        return await self.http.get(f"/links/{link_id_str}")

    async def search(
        self,
        amount_from: Optional[float] = None,
        amount_to: Optional[float] = None,
        creation_time_from: Optional[Union[str, datetime]] = None,
        creation_time_to: Optional[Union[str, datetime]] = None,
        order_id: Optional[str] = None,
        currencies: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sorting: Optional[str] = None,
        skip_count: Optional[int] = None,
        max_result_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск платежных ссылок по различным параметрам.

        Аргументы:
            amount_from: Минимальная сумма платежа
            amount_to: Максимальная сумма платежа
            creation_time_from: Нижняя граница даты создания
            creation_time_to: Верхняя граница даты создания
            order_id: Идентификатор заказа в системе продавца
            currencies: Список валют для фильтрации
            statuses: Список статусов для фильтрации (Opened, Closed)
            sorting: Поле для сортировки (orderId, creationTime, amount)
                     Добавьте суффикс "desc" для сортировки по убыванию
            skip_count: Количество записей для пропуска
            max_result_count: Максимальное количество возвращаемых записей

        Возвращает:
            Словарь, содержащий items (список платежных ссылок) и totalCount

        Пример:
            ```python
            result = await client.links.search(
                amount_from=10.0,
                amount_to=100.0,
                currencies=["RUB"],
                sorting="creationTime desc",
                max_result_count=20
            )
            links = result["items"]
            total = result["totalCount"]
            ```
        """
        params = self._prepare_params(
            amountFrom=amount_from,
            amountTo=amount_to,
            creationTimeFrom=self._format_date_param(creation_time_from),
            creationTimeTo=self._format_date_param(creation_time_to),
            orderId=order_id,
            currencies=self._format_array_param(currencies),
            statuses=self._format_array_param(statuses),
            sorting=sorting,
            skipCount=skip_count,
            maxResultCount=max_result_count,
        )

        self.logger.info("Поиск платежных ссылок")
        return await self.http.get("/links", params=params)
