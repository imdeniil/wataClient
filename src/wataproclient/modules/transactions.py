"""
Модуль для работы с транзакциями WATA API.

Предоставляет интерфейс для получения информации о транзакциях и их поиска.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from uuid import UUID

from .base import BaseApiModule


class TransactionsModule(BaseApiModule):
    """
    Модуль для работы с транзакциями WATA API.
    
    Позволяет получать информацию о транзакциях и осуществлять их поиск
    с применением различных фильтров.
    """

    def __init__(self, http_client):
        """
        Инициализация модуля транзакций.

        Аргументы:
            http_client: Экземпляр HTTP-клиента
        """
        super().__init__(http_client)
        self.logger.debug("TransactionsModule инициализирован.")
        self.base_endpoint = "/api/h2h/transactions"

    async def get(self, transaction_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Получение информации о транзакции по её UUID.

        Аргументы:
            transaction_id: UUID идентификатор транзакции

        Возвращает:
            Словарь с информацией о транзакции, включая:
            - id: UUID идентификатор транзакции в системе WATA
            - terminalName: Название магазина мерчанта
            - terminalPublicId: Публичный идентификатор магазина мерчанта
            - type: Тип транзакции (CardCrypto, SBP)
            - amount: Сумма платежа
            - currency: Валюта платежа (RUB, EUR, USD)
            - status: Статус транзакции (Pending, Paid, Declined)
            - errorCode: Код ошибки в случае неуспешного запроса
            - errorDescription: Описание ошибки в случае неуспешного запроса
            - orderId: Идентификатор заказа в системе мерчанта
            - orderDescription: Описание заказа
            - creationTime: Дата и время создания транзакции в UTC
            - paymentTime: Дата и время оплаты транзакции в UTC
            - totalCommission: Комиссия за транзакцию
            - sbpLink: Ссылка на QR-код (если тип транзакции SBP)
            - paymentLinkId: Идентификатор платежной ссылки (если транзакция создана через ссылку)
        """
        self.logger.info(f"Получение информации о транзакции с ID {transaction_id}")
        
        # Преобразуем UUID в строку, если это необходимо
        if isinstance(transaction_id, UUID):
            transaction_id = str(transaction_id)
        
        # Выполнение запроса
        endpoint = f"{self.base_endpoint}/{transaction_id}"
        return await self.http.get(endpoint)
    
    async def search(
        self,
        order_id: Optional[str] = None,
        creation_time_from: Optional[Union[datetime, str]] = None,
        creation_time_to: Optional[Union[datetime, str]] = None,
        amount_from: Optional[float] = None,
        amount_to: Optional[float] = None,
        currencies: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sorting: Optional[str] = None,
        skip_count: Optional[int] = None,
        max_result_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск транзакций с фильтрацией.

        Аргументы:
            order_id: Идентификатор заказа в системе мерчанта
            creation_time_from: Начальная дата создания
            creation_time_to: Конечная дата создания
            amount_from: Минимальная сумма платежа
            amount_to: Максимальная сумма платежа
            currencies: Список валют (RUB, EUR, USD)
            statuses: Список статусов транзакций (Pending, Paid, Declined)
            sorting: Поле для сортировки (orderId, creationTime, amount)
                     Можно добавить суффикс 'desc' для сортировки по убыванию
            skip_count: Количество записей, которые нужно пропустить (по умолчанию 0)
            max_result_count: Максимальное количество записей (по умолчанию 10, максимум 1000)

        Возвращает:
            Словарь с результатами поиска:
            - items: Список транзакций
            - totalCount: Общее количество найденных записей
        """
        self.logger.info("Поиск транзакций")
        
        # Подготовка параметров запроса
        params = {}
        
        if order_id:
            params["orderId"] = order_id
        if creation_time_from is not None:
            params["creationTimeFrom"] = self._format_date_param(creation_time_from)
        if creation_time_to is not None:
            params["creationTimeTo"] = self._format_date_param(creation_time_to)
        if amount_from is not None:
            params["amountFrom"] = float(amount_from)
        if amount_to is not None:
            params["amountTo"] = float(amount_to)
        if currencies:
            params["currencies"] = self._format_array_param(currencies)
        if statuses:
            params["statuses"] = self._format_array_param(statuses)
        if sorting:
            params["sorting"] = sorting
        if skip_count is not None:
            params["skipCount"] = skip_count
        if max_result_count is not None:
            params["maxResultCount"] = max_result_count
        
        # Выполнение запроса
        return await self.http.get(self.base_endpoint, params=params)
