# WATA Pro API Client

Асинхронный модульный клиент для платежного API WATA Pro.

## Установка

```bash
pip install wataproclient
```

## Быстрый старт

```python
import asyncio
from wataproclient import WataClient

async def main():
    # Инициализация клиента с базовым URL и JWT-токеном
    async with WataClient(
        base_url="https://api.wata.pro",
        jwt_token="ваш_jwt_токен"
    ) as client:
        # Создание платежной ссылки
        payment_link = await client.links.create(
            amount=1188.00,
            currency="RUB",
            description="Оплата заказа №123",
            order_id="ORDER-123",
            success_redirect_url="https://example.com/success",
            fail_redirect_url="https://example.com/fail"
        )
        
        print(f"Создана платежная ссылка: {payment_link['url']}")
        
        # Получение информации о платежной ссылке по ID
        link_info = await client.links.get(payment_link["id"])
        print(f"Статус ссылки: {link_info['status']}")
        
        # Если транзакция уже была создана, можно получить информацию о ней
        try:
            transaction_id = "3a16a4f0-27b0-09d1-16da-ba8d5c63eae3"  # Пример ID транзакции
            transaction = await client.transactions.get(transaction_id)
            print(f"Статус транзакции: {transaction['status']}")
        except Exception as e:
            print(f"Ошибка при получении транзакции: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Возможности клиента

### Платежные ссылки (`client.links`)

```python
# Создание платежной ссылки
link = await client.links.create(
    amount=1000.00,
    currency="RUB",
    description="Описание платежа",
    order_id="ORDER-123",
    success_redirect_url="https://example.com/success",
    fail_redirect_url="https://example.com/fail",
    expiration_date_time="2024-06-01T12:00:00Z"
)

# Получение платежной ссылки по ID
link_info = await client.links.get("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Поиск платежных ссылок
links = await client.links.search(
    amount_from=1000.00,
    amount_to=2000.00,
    currencies=["RUB"],
    statuses=["Opened"],
    sorting="creationTime desc",
    max_result_count=20
)
```

### Транзакции (`client.transactions`)

```python
# Получение транзакции по ID
transaction = await client.transactions.get("3a16a4f0-27b0-09d1-16da-ba8d5c63eae3")

# Поиск транзакций
transactions = await client.transactions.search(
    creation_time_from="2024-05-01T00:00:00Z",
    creation_time_to="2024-05-31T23:59:59Z", 
    currencies=["RUB"],
    statuses=["Paid"],
    sorting="amount desc",
    max_result_count=50
)
```

### Верификация вебхуков (`client.webhooks`)

```python
# Проверка подписи вебхука
is_valid = await client.webhooks.verify_signature(
    raw_json_body=webhook_request_body,  # Сырые байты тела запроса вебхука
    signature_header=webhook_signature   # Значение заголовка X-Signature
)
```

## Обработка ошибок

Клиент предоставляет набор специализированных исключений для обработки различных ошибок API:

```python
from wataproclient import (
    ApiError,              # Базовое исключение
    ApiConnectionError,    # Ошибка соединения
    ApiTimeoutError,       # Тайм-аут запроса
    ApiAuthError,          # Ошибка аутентификации
    ApiForbiddenError,     # Доступ запрещен
    ApiResourceNotFoundError,  # Ресурс не найден
    ApiValidationError,    # Ошибка валидации
    ApiServerError,        # Ошибка сервера
    ApiServiceUnavailableError,  # Сервис недоступен
    ApiParsingError,       # Ошибка парсинга ответа
)

try:
    result = await client.links.create(amount=1000.00, currency="RUB")
except ApiAuthError:
    print("Ошибка аутентификации. Проверьте JWT-токен")
except ApiValidationError as e:
    print(f"Ошибка валидации: {e.message}")
except ApiConnectionError:
    print("Не удалось подключиться к API")
except ApiError as e:  # Перехватывает все ошибки API
    print(f"Ошибка API: {e.message}, код: {e.status_code}")
```

## Расширенная конфигурация

```python
# Расширенная конфигурация клиента
client = WataClient(
    base_url="https://api.wata.pro",
    jwt_token="ваш_jwt_токен",
    timeout=60,  # Таймаут запроса в секундах
    max_retries=5,  # Максимальное количество повторных попыток
    log_level=logging.DEBUG  # Уровень логирования
)

# Использование менеджера клиентов для управления несколькими экземплярами
from wataproclient import WataClientManager

# Регистрация клиента
WataClientManager.register("prod", client)

# Получение клиента по имени
prod_client = WataClientManager.get("prod")

# Проверка существования клиента
if WataClientManager.exists("prod"):
    # Использование клиента...
    pass

# Закрытие всех клиентов
await WataClientManager.close_all()
```

## Требования

- Python 3.7+
- aiohttp 3.7.4+
- cryptography

## Лицензия

MIT
