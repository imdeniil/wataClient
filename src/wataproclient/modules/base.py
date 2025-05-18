"""
Базовый модуль для WATA API.
"""
import logging
from abc import ABC
from typing import Any, Dict, Optional

from ..http import AsyncHttpClient


class BaseApiModule(ABC):
    """Базовый класс для всех модулей API."""

    def __init__(self, http_client: AsyncHttpClient):
        """
        Инициализация модуля API.

        Аргументы:
            http_client: Экземпляр HTTP-клиента
        """
        self.http = http_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def _debug_log_method_call(self, method_name: str, **kwargs):
        """
        Логирование вызова метода API в debug режиме.
        
        Аргументы:
            method_name: Название метода
            **kwargs: Параметры метода
        """
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"*** ВЫЗОВ МЕТОДА {self.__class__.__name__}.{method_name} ***")
            for key, value in kwargs.items():
                if value is not None:
                    self.logger.debug(f"  {key}: {value}")
            self.logger.debug(f"*** КОНЕЦ ПАРАМЕТРОВ МЕТОДА ***")
    
    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """
        Подготовка параметров запроса путём удаления значений None.

        Аргументы:
            **kwargs: Параметры для подготовки

        Возвращает:
            Словарь с параметрами, отличными от None
        """
        return {k: v for k, v in kwargs.items() if v is not None}
    
    def _format_date_param(self, date_obj: Any) -> Optional[str]:
        """
        Форматирование объекта даты в строку ISO 8601 для API-запросов.

        Аргументы:
            date_obj: Объект даты или строка

        Возвращает:
            Отформатированная строка даты или None, если входные данные - None
        """
        if date_obj is None:
            return None
            
        # Если это уже строка, предполагаем, что она правильно отформатирована
        if isinstance(date_obj, str):
            return date_obj
            
        # Если у объекта есть метод isoformat (datetime, date), используем его
        if hasattr(date_obj, 'isoformat'):
            return date_obj.isoformat()
            
        # В крайнем случае, преобразуем в строку
        return str(date_obj)

    def _format_array_param(self, values: Optional[list]) -> Optional[str]:
        """
        Форматирование списковых параметров в строки, разделенные запятыми, для API-запросов.

        Аргументы:
            values: Список значений или None

        Возвращает:
            Строка, разделенная запятыми, или None, если входные данные - None
        """
        if values is None:
            return None
            
        return ','.join(str(v) for v in values)
