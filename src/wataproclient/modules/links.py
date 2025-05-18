"""
Модуль для работы с платежными ссылками WATA API.

Предоставляет интерфейс для создания, получения и поиска платежных ссылок.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from uuid import UUID

from .base import BaseApiModule


class LinksModule(BaseApiModule):
    """
    Модуль для работы с платежными ссылками WATA API.
    
    Позволяет создавать, получать и искать платежные ссылки.
    Платежные ссылки используются для сценария, когда платежная форма 
    находится на стороне WATA. Ссылка одноразовая и становится недействительной 
    после первой успешной оплаты.
    """

    def __init__(self, http_client):
        """
        Инициализация модуля платежных ссылок.

        Аргументы:
            http_client: Экземпляр HTTP-клиента
        """
        super().__init__(http_client)
        self.logger.debug("LinksModule инициализирован.")
        self.base_endpoint = "/api/h2h/links"

    async def create(
        self,
        amount: float,
        currency: str,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        success_redirect_url: Optional[str] = None,
        fail_redirect_url: Optional[str] = None,
        expiration_date_time: Optional[Union[datetime, str]] = None,
    ) -> Dict[str, Any]:
        """
        Создание платежной ссылки.

        Платежная ссылка одноразовая и становится недействительной 
        после первой успешной оплаты.

        Аргументы:
            amount: Сумма платежа (например, 1188.00)
            currency: Валюта платежа (RUB, EUR, USD)
            description: Описание заказа
            order_id: Идентификатор заказа в системе мерчанта
            success_redirect_url: URL для перенаправления при успешной оплате
            fail_redirect_url: URL для перенаправления при ошибке оплаты
            expiration_date_time: Время жизни платежной ссылки (по умолчанию 3 дня, максимум 30 дней)

        Возвращает:
            Словарь с информацией о созданной платежной ссылке, включая:
            - id: UUID идентификатор заказа в системе WATA
            - amount: Сумма платежа
            - currency: Валюта платежа
            - status: Статус платежной ссылки (Opened, Closed)
            - url: Адрес платежной ссылки
            - terminalName: Название магазина мерчанта
            - terminalPublicId: Идентификатор магазина мерчанта
            - creationTime: Дата и время создания ссылки
            - orderId: Идентификатор заказа в системе мерчанта
            - description: Описание заказа
            - successRedirectUrl: URL для перенаправления при успешной оплате
            - failRedirectUrl: URL для перенаправления при ошибке оплаты
            - expirationDateTime: Время жизни платежной ссылки
        """
        # Логирование вызова метода в debug режиме
        self._debug_log_method_call(
            "create",
            amount=amount,
            currency=currency,
            description=description,
            order_id=order_id,
            success_redirect_url=success_redirect_url,
            fail_redirect_url=fail_redirect_url,
            expiration_date_time=expiration_date_time
        )
        
        self.logger.info(f"Создание платежной ссылки на сумму {amount} {currency}")
        
        # Подготовка данных запроса
        data = {
            "amount": float(amount),
            "currency": currency,
        }
        
        # Добавление опциональных параметров
        if description:
            data["description"] = description
        if order_id:
            data["orderId"] = order_id
        if success_redirect_url:
            data["successRedirectUrl"] = success_redirect_url
        if fail_redirect_url:
            data["failRedirectUrl"] = fail_redirect_url
        if expiration_date_time:
            data["expirationDateTime"] = self._format_date_param(expiration_date_time)
        
        # Логирование подготовленных данных в debug режиме
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Конечная точка: {self.base_endpoint}")
            self.logger.debug(f"Подготовленные данные для отправки: {data}")
        
        # Выполнение запроса
        result = await self.http.post(self.base_endpoint, data=data)
        
        # Логирование результата в debug режиме
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Результат создания платежной ссылки: {result}")
        
        return result
    
    async def get(self, link_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Получение информации о платежной ссылке по её UUID.

        Аргументы:
            link_id: UUID идентификатор платежной ссылки

        Возвращает:
            Словарь с информацией о платежной ссылке, включая:
            - id: UUID идентификатор заказа в системе WATA
            - amount: Сумма платежа
            - currency: Валюта платежа
            - status: Статус платежной ссылки (Opened, Closed)
            - url: Адрес платежной ссылки
            - terminalName: Название магазина мерчанта
            - terminalPublicId: Идентификатор магазина мерчанта
            - creationTime: Дата и время создания ссылки
            - orderId: Идентификатор заказа в системе мерчанта
            - description: Описание заказа
            - successRedirectUrl: URL для перенаправления при успешной оплате
            - failRedirectUrl: URL для перенаправления при ошибке оплаты
            - expirationDateTime: Время жизни платежной ссылки
        """
        # Логирование вызова метода в debug режиме
        self._debug_log_method_call("get", link_id=link_id)
        
        self.logger.info(f"Получение информации о платежной ссылке с ID {link_id}")
        
        # Преобразуем UUID в строку, если это необходимо
        if isinstance(link_id, UUID):
            link_id = str(link_id)
        
        # Логирование конечной точки в debug режиме
        endpoint = f"{self.base_endpoint}/{link_id}"
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Конечная точка: {endpoint}")
        
        # Выполнение запроса
        result = await self.http.get(endpoint)
        
        # Логирование результата в debug режиме
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Результат получения платежной ссылки: {result}")
        
        return result
    
    async def search(
        self,
        amount_from: Optional[float] = None,
        amount_to: Optional[float] = None,
        creation_time_from: Optional[Union[datetime, str]] = None,
        creation_time_to: Optional[Union[datetime, str]] = None,
        order_id: Optional[str] = None,
        currencies: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sorting: Optional[str] = None,
        skip_count: Optional[int] = None,
        max_result_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск платежных ссылок с фильтрацией.

        Аргументы:
            amount_from: Минимальная сумма платежа
            amount_to: Максимальная сумма платежа
            creation_time_from: Начальная дата создания
            creation_time_to: Конечная дата создания
            order_id: Идентификатор заказа в системе мерчанта
            currencies: Список валют (RUB, EUR, USD)
            statuses: Список статусов (Opened, Closed)
            sorting: Поле для сортировки (orderId, creationTime, amount)
                     Можно добавить суффикс 'desc' для сортировки по убыванию
            skip_count: Количество записей, которые нужно пропустить (по умолчанию 0)
            max_result_count: Максимальное количество записей (по умолчанию 10, максимум 1000)

        Возвращает:
            Словарь с результатами поиска:
            - items: Список платежных ссылок
            - totalCount: Общее количество найденных записей
        """
        # Логирование вызова метода в debug режиме
        self._debug_log_method_call(
            "search",
            amount_from=amount_from,
            amount_to=amount_to,
            creation_time_from=creation_time_from,
            creation_time_to=creation_time_to,
            order_id=order_id,
            currencies=currencies,
            statuses=statuses,
            sorting=sorting,
            skip_count=skip_count,
            max_result_count=max_result_count
        )
        
        self.logger.info("Поиск платежных ссылок")
        
        # Подготовка параметров запроса
        params = {}
        
        if amount_from is not None:
            params["amountFrom"] = float(amount_from)
        if amount_to is not None:
            params["amountTo"] = float(amount_to)
        if creation_time_from is not None:
            params["creationTimeFrom"] = self._format_date_param(creation_time_from)
        if creation_time_to is not None:
            params["creationTimeTo"] = self._format_date_param(creation_time_to)
        if order_id:
            params["orderId"] = order_id
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
        
        # Логирование подготовленных параметров в debug режиме
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Конечная точка: {self.base_endpoint}")
            self.logger.debug(f"Подготовленные параметры: {params}")
        
        # Выполнение запроса
        result = await self.http.get(self.base_endpoint, params=params)
        
        # Логирование результата в debug режиме
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Результат поиска платежных ссылок: {result}")
        
        return result
