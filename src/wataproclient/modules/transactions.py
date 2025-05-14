"""
Модуль для работы с транзакциями.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .base import BaseApiModule

class TransactionsModule(BaseApiModule):
    """Модуль для работы с транзакциями."""

    async def get(self, transaction_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Получение деталей транзакции по ID.

        Аргументы:
            transaction_id: UUID транзакции

        Возвращает:
            Детали транзакции

        Пример:
            ```python
            transaction = await client.transactions.get("550e8400-e29b-41d4-a716-446655440000")
            print(f"Статус транзакции: {transaction['status']}")
            ```
        """
        transaction_id_str = str(transaction_id)
        self.logger.info(f"Получение транзакции {transaction_id_str}")
        return await self.http.get(f"/transactions/{transaction_id_str}")

    async def search(
        self,
        order_id: Optional[str] = None,
        creation_time_from: Optional[Union[str, datetime]] = None,
        creation_time_to: Optional[Union[str, datetime]] = None,
        amount_from: Optional[float] = None,
        amount_to: Optional[float] = None,
        currencies: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sorting: Optional[str] = None,
        skip_count: Optional[int] = None,
        max_result_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск транзакций по различным параметрам.

        Аргументы:
            order_id: Идентификатор заказа в системе продавца
            creation_time_from: Нижняя граница даты создания
            creation_time_to: Верхняя граница даты создания
            amount_from: Минимальная сумма транзакции
            amount_to: Максимальная сумма транзакции
            currencies: Список валют для фильтрации
            statuses: Список статусов для фильтрации (Pending, Paid, Declined)
            sorting: Поле для сортировки (amount, creationTime)
                     Добавьте суффикс "desc" для сортировки по убыванию
            skip_count: Количество записей для пропуска
            max_result_count: Максимальное количество возвращаемых записей

        Возвращает:
            Словарь, содержащий items (список транзакций) и totalCount

        Пример:
            ```python
            result = await client.transactions.search(
                amount_from=10.0,
                amount_to=100.0,
                currencies=["RUB"],
                statuses=["Paid"],
                sorting="creationTime desc",
                max_result_count=20
            )
            transactions = result["items"]
            total = result["totalCount"]
            ```
        """
        params = self._prepare_params(
            orderId=order_id,
            creationTimeFrom=self._format_date_param(creation_time_from),
            creationTimeTo=self._format_date_param(creation_time_to),
            amountFrom=amount_from,
            amountTo=amount_to,
            currencies=self._format_array_param(currencies),
            statuses=self._format_array_param(statuses),
            sorting=sorting,
            skipCount=skip_count,
            maxResultCount=max_result_count,
        )

        self.logger.info("Поиск транзакций")
        return await self.http.get("/transactions", params=params)
