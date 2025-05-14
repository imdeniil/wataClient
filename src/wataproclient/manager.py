"""
Менеджер клиентов WATA API.

Предоставляет централизованное управление экземплярами WataClient.
"""
import logging
from typing import Dict, Optional

from .client import WataClient

class WataClientManager:
    """
    Менеджер клиентов WATA API.
    
    Позволяет регистрировать и получать доступ к экземплярам WataClient
    с разными конфигурациями.
    """
    _clients: Dict[str, WataClient] = {}
    _logger = logging.getLogger("wata_client_manager")
    
    @classmethod
    def register(cls, name: str, client: WataClient) -> WataClient:
        """
        Регистрирует экземпляр клиента с указанным именем.
        
        Args:
            name: Уникальное имя клиента
            client: Экземпляр WataClient
            
        Returns:
            Зарегистрированный клиент
            
        Raises:
            ValueError: Если клиент с таким именем уже существует
        """
        if name in cls._clients:
            raise ValueError(f"Клиент с именем '{name}' уже зарегистрирован")
            
        cls._clients[name] = client
        cls._logger.info(f"Зарегистрирован клиент с именем '{name}'")
        return client
    
    @classmethod
    def create(cls, name: str, **config) -> WataClient:
        """
        Создает и регистрирует новый клиент с указанной конфигурацией.
        
        Args:
            name: Уникальное имя клиента
            **config: Параметры конфигурации для WataClient
            
        Returns:
            Созданный экземпляр WataClient
            
        Raises:
            ValueError: Если клиент с таким именем уже существует
        """
        client = WataClient(**config)
        return cls.register(name, client)
    
    @classmethod
    def get(cls, name: str) -> WataClient:
        """
        Получает зарегистрированный клиент по имени.
        
        Args:
            name: Имя клиента
            
        Returns:
            Экземпляр WataClient
            
        Raises:
            KeyError: Если клиент с указанным именем не найден
        """
        if name not in cls._clients:
            raise KeyError(f"Клиент с именем '{name}' не зарегистрирован")
            
        return cls._clients[name]
    
    @classmethod
    def exists(cls, name: str) -> bool:
        """
        Проверяет, существует ли клиент с указанным именем.
        
        Args:
            name: Имя клиента
            
        Returns:
            True, если клиент существует, иначе False
        """
        return name in cls._clients
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Удаляет клиент из реестра (без закрытия сессии).
        
        Args:
            name: Имя клиента
            
        Raises:
            KeyError: Если клиент с указанным именем не найден
        """
        if name not in cls._clients:
            raise KeyError(f"Клиент с именем '{name}' не зарегистрирован")
            
        del cls._clients[name]
        cls._logger.info(f"Клиент с именем '{name}' удален из реестра")
    
    @classmethod
    async def close(cls, name: str) -> None:
        """
        Закрывает клиент и удаляет его из реестра.
        
        Args:
            name: Имя клиента
            
        Raises:
            KeyError: Если клиент с указанным именем не найден
        """
        if name not in cls._clients:
            raise KeyError(f"Клиент с именем '{name}' не зарегистрирован")
            
        await cls._clients[name].close()
        del cls._clients[name]
        cls._logger.info(f"Клиент с именем '{name}' закрыт и удален из реестра")
    
    @classmethod
    async def close_all(cls) -> None:
        """
        Закрывает все зарегистрированные клиенты.
        """
        for name in list(cls._clients.keys()):
            await cls._clients[name].close()
            
        cls._clients.clear()
        cls._logger.info("Все клиенты закрыты и удалены из реестра")
