#!/usr/bin/env python
"""
Тестовый скрипт для проверки подробного логирования в debug режиме.
"""
import asyncio
import logging
import uuid
from wataproclient import WataClientManager, ApiError
from env import WATATOKEN  # Ваш токен

# Функция для создания уникального ID
def create_prefixed_uuid(prefix):
    return f"{prefix}-{uuid.uuid4()}"

# Настройка детального логирования
def setup_detailed_logging():
    """Настройка подробного логирования с форматированием."""
    # Создаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Убираем все существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Создаем подробный форматтер
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(detailed_formatter)
    
    # Добавляем обработчик к корневому логгеру
    root_logger.addHandler(console_handler)
    
    print("=== ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ВКЛЮЧЕНО ===")
    print("Уровень логирования: DEBUG")
    print("Вы увидите подробную информацию о каждом HTTP-запросе\n")

async def main():
    """Основная функция для тестирования."""
    print("=== НАЧАЛО ТЕСТИРОВАНИЯ КЛИЕНТА WATA ===\n")
    
    # Настройка логирования
    setup_detailed_logging()
    
    # Создание клиента с debug логированием
    print("Создание клиента с debug логированием...")
    WataClientManager.create(
        name="debug_test", 
        base_url="https://api.wata.pro",  # Исправленный URL
        jwt_token=WATATOKEN,
        timeout=30,
        max_retries=3,
        log_level=logging.DEBUG  # Включаем debug логирование
    )
    
    wata = WataClientManager.get("debug_test")
    print("Клиент создан успешно\n")
    
    try: 
        async with wata:
            print("=== ТЕСТ 1: СОЗДАНИЕ ПЛАТЕЖНОЙ ССЫЛКИ ===")
            result = await wata.links.create(
                amount=10.00, 
                currency="RUB", 
                description="Тестовый платеж с debug логированием", 
                order_id=create_prefixed_uuid("debug"),
                success_redirect_url="https://vk.com",
                fail_redirect_url="https://google.com"
            )
            print(f"✅ Создание прошло успешно!")
            print(f"Ссылка: {result.get('url', 'URL не найден')}")
            print(f"ID: {result.get('id', 'ID не найден')}\n")
            
            # Небольшая пауза для разделения логов
            await asyncio.sleep(1)
            
            print("=== ТЕСТ 2: ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ССЫЛКЕ ===")
            link_id = result.get('id')
            if link_id:
                get_result = await wata.links.get(link_id)
                print(f"✅ Получение информации прошло успешно!")
                print(f"Статус: {get_result.get('status', 'Статус не найден')}")
                print(f"Сумма: {get_result.get('amount', 'Сумма не найдена')} {get_result.get('currency', '')}\n")
            else:
                print("❌ Не удалось получить ID созданной ссылки\n")
            
            # Небольшая пауза для разделения логов
            await asyncio.sleep(1)
            
            print("=== ТЕСТ 3: ПОИСК ПЛАТЕЖНЫХ ССЫЛОК ===")
            search_result = await wata.links.search(
                amount_from=5.00,
                amount_to=50.00,
                currencies=["RUB"],
                sorting="creationTime desc",
                max_result_count=3
            )
            total_count = search_result.get('totalCount', 0)
            print(f"✅ Поиск завершен успешно!")
            print(f"Найдено ссылок: {total_count}")
            
            if total_count > 0:
                items = search_result.get('items', [])
                print("Последние ссылки:")
                for i, item in enumerate(items[:3], 1):
                    print(f"  {i}. ID: {item.get('id', 'N/A')}, "
                          f"Сумма: {item.get('amount', 'N/A')} {item.get('currency', 'N/A')}")
            print()
    
    except ApiError as e:
        print(f"❌ ОШИБКА API:")
        print(f"   Статус: {e.status_code}")
        print(f"   Сообщение: {e.message}")
        print(f"   Детали: {e.response_data}")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
    
    finally:
        # Закрытие всех клиентов
        await WataClientManager.close_all()
        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

if __name__ == "__main__":
    asyncio.run(main())
