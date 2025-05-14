#!/usr/bin/env python
"""
Примеры использования клиента WATA API.

Рекомендуемый способ запуска с использованием uv:
uv run python example.py
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Импорт из src
from src.wataproclient import WataClient, ApiError, ApiResourceNotFoundError


async def simple_example():
    """Простой пример использования клиента WATA API."""
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Получение учетных данных API из переменных окружения
    jwt_token = os.getenv("WATA_JWT_TOKEN", "ваш-токен-здесь")
    
    print("Запуск простого примера...")
    # Создание экземпляра клиента
    print("Инициализация WATA клиента...")
    async with WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",  # Песочница
        jwt_token=jwt_token,
        timeout=30,
        max_retries=3,
        log_level=logging.INFO,
    ) as client:
        print("Клиент инициализирован успешно!")
        
        # Пример 1: Получение публичного ключа
        try:
            print("\n1. Получение публичного ключа...")
            public_key = await client.payments.get_public_key()
            print(f"Публичный ключ получен: {public_key.get('key', 'Ключ не найден')}")
        except Exception as e:
            print(f"Ошибка при получении публичного ключа: {e}")

        # Пример 2: Создание платежной ссылки
        try:
            print("\n2. Создание платежной ссылки...")
            payment_link = await client.links.create(
                amount=100.50,
                currency="RUB",
                order_id="TEST-123",
                description="Тестовый платеж",
                success_url="https://example.com/success",
                fail_url="https://example.com/fail"
            )
            print(f"Создана платежная ссылка: {payment_link.get('url', 'URL не найден')}")
        except Exception as e:
            print(f"Ошибка при создании платежной ссылки: {e}")

        # Пример 3: Поиск платежных ссылок
        try:
            print("\n3. Поиск платежных ссылок...")
            search_result = await client.links.search(
                amount_from=50.0,
                amount_to=150.0,
                currencies=["RUB"],
                sorting="creationTime desc",
                max_result_count=5
            )
            total_count = search_result.get('totalCount', 0)
            print(f"Найдено {total_count} платежных ссылок")
            
            if total_count > 0:
                print("\nСписок платежных ссылок:")
                for link in search_result.get("items", []):
                    print(f"ID: {link.get('id')}, Сумма: {link.get('amount')} {link.get('currency')}")
        except Exception as e:
            print(f"Ошибка при поиске платежных ссылок: {e}")

        # Пример 4: Обработка ошибок
        try:
            print("\n4. Обработка ошибок...")
            # Попытка получить несуществующую платежную ссылку
            payment_link = await client.links.get("несуществующий-id")
            print(f"Платежная ссылка найдена: {payment_link}")
        except ApiResourceNotFoundError as e:
            print(f"Платежная ссылка не найдена: {e}")
        except ApiError as e:
            print(f"Произошла ошибка API: {e}")
    
    print("Простой пример завершен!")


async def process_payment(client, order_id, amount, description):
    """Вспомогательная функция для обработки платежа."""
    try:
        payment_link = await client.links.create(
            amount=amount,
            currency="RUB",
            order_id=order_id,
            description=description,
            success_url="https://example.com/success",
            fail_url="https://example.com/fail"
        )
        print(f"Для заказа {order_id} создана платежная ссылка: {payment_link['url']}")
        return payment_link
    except Exception as e:
        print(f"Ошибка при создании платежной ссылки для заказа {order_id}: {e}")
        return None


async def multi_client_example():
    """Пример использования нескольких экземпляров клиента WATA API."""
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    print("\nЗапуск примера с несколькими клиентами...")
    
    # Получение учетных данных API из переменных окружения
    jwt_token = os.getenv("WATA_JWT_TOKEN", "ваш-токен-здесь")
    
    # Создание первого экземпляра клиента (песочница)
    print("Инициализация клиента 1 (песочница)...")
    sandbox_client = WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",
        jwt_token=jwt_token,
        timeout=30,
        max_retries=3,
        log_level=logging.INFO,
    )
    
    # Создание второго экземпляра клиента (с другими настройками)
    print("Инициализация клиента 2 (продакшн)...")
    production_client = WataClient(
        base_url="https://api.wata.pro/api/h2h",  # Реальный API
        jwt_token=jwt_token,
        timeout=60,  # Увеличенный таймаут
        max_retries=5,  # Больше повторных попыток
        log_level=logging.WARNING,  # Другой уровень логирования
    )
    
    try:
        # Параллельное использование обоих клиентов
        print("Использование обоих клиентов параллельно...")
        async with sandbox_client, production_client:
            # Список задач для запуска
            tasks = [
                process_payment(sandbox_client, "SANDBOX-123", 100.50, "Тестовый платеж в песочнице"),
                process_payment(sandbox_client, "SANDBOX-124", 200.75, "Второй тестовый платеж в песочнице"),
                # В реальном сценарии вы бы использовали production_client только в продакшн-среде
                # Здесь мы используем его для демонстрации
                process_payment(production_client, "PROD-123", 100.50, "Тестовый платеж в продакшн")
            ]
            
            # Запуск задач параллельно
            start_time = datetime.now()
            results = await asyncio.gather(*tasks)
            end_time = datetime.now()
            
            # Вывод результатов
            print(f"\nРезультаты параллельной обработки:")
            print(f"Успешно обработано: {sum(1 for r in results if r is not None)} из {len(results)}")
            print(f"Время выполнения: {(end_time - start_time).total_seconds():.2f} секунд")
            
            # Поиск платежных ссылок в песочнице
            search_result = await sandbox_client.links.search(
                amount_from=50.0,
                amount_to=250.0,
                currencies=["RUB"],
                sorting="creationTime desc",
                max_result_count=5
            )
            print(f"\nНайдено {search_result.get('totalCount', 0)} платежных ссылок в песочнице")
            
    except Exception as e:
        print(f"Произошла глобальная ошибка: {e}")
    
    print("Пример с несколькими клиентами завершен!")

async def webhook_verification_example():
    """
    Пример симулированной проверки подписи вебхука WATA.

    Этот пример НЕ запускает реальный веб-сервер и НЕ принимает реальный вебхук.
    Он демонстрирует, как использовать метод client.webhooks.verify_signature
    с предопределенными тестовыми данными вебхука и заголовком подписи.

    В реальном приложении этот код должен быть частью обработчика HTTP POST запроса,
    принимающего вебхуки от WATA.
    """
    print("\n" + "=" * 80)
    print("ПРИМЕР СИМУЛИРОВАННОЙ ПРОВЕРКИ ПОДПИСИ ВЕБХУКА")
    print("=" * 80)

    # Загрузка переменных окружения и настройка логирования (если еще не сделано в main или вызывающей функции)
    # load_dotenv()
    # logging.basicConfig(level=logging.INFO)

    jwt_token = os.getenv("WATA_JWT_TOKEN", "ваш-токен-здесь")

    print("Инициализация WATA клиента для примера проверки вебхука...")
    async with WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",  # Или ваш реальный URL API, откуда получается публичный ключ
        jwt_token=jwt_token, # JWT токен не нужен для самой верификации подписи, но нужен клиенту для получения ключа
        timeout=30,
        max_retries=3,
        log_level=logging.INFO,
    ) as client:
        print("Клиент инициализирован успешно.")

        # --- Симуляция получения данных вебхука ---
        # В реальном обработчике вебхука вы бы получили эти данные из входящего HTTP запроса:
        # raw_body = await request.read() # Сырое тело запроса в байтах
        # signature_header = request.headers.get("X-Signature") # Значение заголовка X-Signature

        # Используем пример тела вебхука из документации (как байты)
        # Важно: строка должна быть EXACTLY как в raw JSON, включая пробелы и переносы строк
        # Используем decode() с 'utf-8' для получения строки, затем encode() обратно в байты
        # или просто определяем ее как байтовый литерал b"..."
        simulated_raw_body_str = """{
  "transactionType": "CardCrypto",
  "transactionId": "3a16a4f0-27b0-09d1-16da-ba8d5c63eae3",
  "transactionStatus": "Paid",
  "errorCode": null,
  "errorDescription": null,
  "terminalName": "string",
  "amount": 1188.00,
  "currency": "RUB",
  "orderId": "string",
  "orderDescription": "string ",
  "paymentTime": "2024-12-04T17:41:44.434598Z ",
  "commission": 10,
  "email": null
}"""
        simulated_raw_body = simulated_raw_body_str.encode('utf-8')

        # Используем фиктивное значение подписи, так как у нас нет приватного ключа WATA для ее генерации.
        # Проверка с такой подписью, вероятно, завершится неудачей (вернет False),
        # что корректно для демонстрации обработки неверной подписи.
        simulated_signature_header = "THIS_IS_A_FAKE_SIGNATURE_FOR_DEMO_PURPOSES_ONLY"
        # Если у вас есть реальный тестовый вебхук с WATA, вы можете вставить сюда его реальный X-Signature.

        print("\nСимуляция проверки подписи вебхука:")
        print(f"Симулированное тело запроса (начало):\n{simulated_raw_body[:200]}...")
        print(f"Симулированный заголовок X-Signature: {simulated_signature_header}")


        # --- Вызов метода верификации ---
        try:
            # Метод verify_signature теперь сам получает и кэширует публичный ключ при первом вызове.
            is_valid = await client.webhooks.verify_signature(
                raw_json_body=simulated_raw_body,
                signature_header=simulated_signature_header
            )

            if is_valid:
                print("\nРезультат проверки подписи: ПОДПИСЬ ВЕРНА.")
                # В реальном сценарии здесь вы бы распарсили JSON и обработали вебхук:
                # webhook_data = json.loads(simulated_raw_body)
                # print("Данные вебхука (после успешной проверки):", webhook_data)
                # ... ваша логика обработки ...
            else:
                print("\nРезультат проверки подписи: ПОДПИСЬ НЕВЕРНА.")
                print("В реальном сценарии следует отклонить этот вебхук (вернуть статус 403).")

        except Exception as e:
            print(f"\nПроизошла ошибка при выполнении проверки подписи: {e}")
            print("Возможно, не удалось получить публичный ключ или другая проблема.")


    print("\nСимулированная проверка подписи вебхука завершена.")



async def main():
    """Запуск всех примеров."""
    print("=" * 80)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ WATA API КЛИЕНТА")
    print("=" * 80)
    
    # Запуск простого примера
    await simple_example()
    
    # Запуск примера с несколькими клиентами
    await multi_client_example()
    
    print("\nВсе примеры успешно выполнены!")


if __name__ == "__main__":
    asyncio.run(main())
