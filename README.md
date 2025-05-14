# Клиент платежного API WATA

Модульный асинхронный Python-клиент для взаимодействия с платежным API WATA.

## Возможности

- Полностью асинхронный API с поддержкой `async`/`await`
- Модульная архитектура для простоты расширения
- Комплексная обработка ошибок со специализированными исключениями
- Автоматические повторные попытки для временных ошибок
- Поддержка JWT-аутентификации
- Подробное логирование
- Аннотации типов для лучшей поддержки IDE и статического анализа
- Поддержка нескольких независимых экземпляров клиента в одном приложении
- Построен с использованием uv — сверхбыстрого пакетного менеджера для Python

## Установка

### Установка с использованием uv (рекомендуется)

```bash
# Установить пакет
uv pip install wataproclient

## Структура проекта

```
wataClient/
├── .python-version        # Используемая версия Python
├── pyproject.toml         # Конфигурация проекта
├── README.md              # Данный файл
├── example.py             # Примеры использования
└── src/                   # Исходный код пакета
    └── wataClient/        # Основной пакет
        ├── __init__.py    # Экспорты пакета
        ├── client.py      # Основной класс клиента
        ├── exceptions.py  # Иерархия исключений
        ├── http.py        # HTTP-клиент
        └── modules/       # Модули API
            ├── __init__.py
            ├── base.py    # Базовый класс модуля
            ├── links.py   # Модуль для работы с платежными ссылками
            ├── payments.py # Модуль для работы с платежами
            └── transactions.py # Модуль для работы с транзакциями
```

## Использование

### Базовое использование

```python
import asyncio
import logging
from src.wataClient import WataClient

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание экземпляра клиента
    async with WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",  # Среда песочницы
        jwt_token="ваш-токен-здесь",
        timeout=30,
        max_retries=3
    ) as client:
        # Создание платежной ссылки
        payment_link = await client.links.create(
            amount=100.50,
            currency="RUB",
            order_id="ORDER-123",
            description="Тестовый платеж",
            success_url="https://example.com/success",
            fail_url="https://example.com/fail"
        )
        
        print(f"Создана платежная ссылка: {payment_link['url']}")
        
        # Поиск платежных ссылок
        search_result = await client.links.search(
            amount_from=50.0,
            amount_to=150.0,
            currencies=["RUB"],
            sorting="creationTime desc",
            max_result_count=5
        )
        
        print(f"Найдено {search_result['totalCount']} платежных ссылок")
        for link in search_result.get("items", []):
            print(f"ID ссылки: {link['id']}, Сумма: {link['amount']} {link['currency']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Использование нескольких экземпляров клиента

Вы можете создать несколько экземпляров клиента WATA API с различными конфигурациями и использовать их независимо друг от друга:

```python
import asyncio
import logging
from src.wataClient import WataClient

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание экземпляров клиента с разными конфигурациями
    sandbox_client = WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",  # Песочница
        jwt_token="токен-для-песочницы",
        timeout=30,
        max_retries=3
    )
    
    production_client = WataClient(
        base_url="https://api.wata.pro/api/h2h",  # Продакшн
        jwt_token="токен-для-продакшн",
        timeout=60,  # Увеличенный таймаут
        max_retries=5  # Больше повторных попыток
    )
    
    # Использование клиентов с контекстным менеджером
    async with sandbox_client, production_client:
        # Параллельное выполнение операций с разными клиентами
        sandbox_tasks = [
            sandbox_client.links.create(
                amount=100.50,
                currency="RUB",
                order_id="SANDBOX-123",
                description="Тестовый платеж в песочнице"
            ),
            sandbox_client.links.search(currencies=["RUB"])
        ]
        
        # При необходимости вы можете выполнять операции параллельно
        sandbox_results = await asyncio.gather(*sandbox_tasks)
        
        # Одновременно выполнять операции с production клиентом
        prod_public_key = await production_client.payments.get_public_key()
```

### Обработка ошибок

```python
import asyncio
from src.wataClient import WataClient, ApiError, ApiResourceNotFoundError

async def main():
    async with WataClient(
        base_url="https://api-sandbox.wata.pro/api/h2h",
        jwt_token="ваш-токен-здесь"
    ) as client:
        try:
            # Попытка получить несуществующую платежную ссылку
            payment_link = await client.links.get("несуществующий-id")
        except ApiResourceNotFoundError as e:
            print(f"Платежная ссылка не найдена: {e}")
        except ApiError as e:
            print(f"Ошибка API: {e}")
```

## Модули API

Клиент разделен на несколько модулей, каждый из которых отвечает за различные аспекты API:

### Модуль Links

Для работы с платежными ссылками:

```python
# Создание платежной ссылки
link = await client.links.create(
    amount=100.50,
    currency="RUB",
    order_id="ORDER-123",
    description="Премиум-подписка"
)

# Получение платежной ссылки по ID
link = await client.links.get("550e8400-e29b-41d4-a716-446655440000")

# Поиск платежных ссылок
links = await client.links.search(
    amount_from=10.0,
    amount_to=100.0,
    currencies=["RUB"],
    sorting="creationTime desc"
)
```

### Модуль Payments

Для создания платежных транзакций:

```python
# Создание карточной транзакции
transaction = await client.payments.create_card_transaction(
    amount=100.50,
    currency="RUB",
    order_id="ORDER-123",
    crypto="ВАШ_КРИПТОГРАММА",
    ip_address="192.168.1.1",
    browser_data={
        "colorDepth": 24,
        "javaEnabled": False,
        "language": "ru-RU",
        "screenHeight": 1080,
        "screenWidth": 1920,
        "timezone": -180,
        "userAgent": "Mozilla/5.0..."
    }
)

# Создание СБП-транзакции
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
    }
)

# Получение публичного ключа для проверки подписи
public_key = await client.payments.get_public_key()
```

### Модуль Transactions

Для работы с транзакциями:

```python
# Получение транзакции по ID
transaction = await client.transactions.get("550e8400-e29b-41d4-a716-446655440000")

# Поиск транзакций
transactions = await client.transactions.search(
    amount_from=10.0,
    amount_to=100.0,
    currencies=["RUB"],
    statuses=["Paid"]
)
```

### Модуль Webhooks

Для проверки подписи вебхуков:

```python
# Проверка подписи вебхука
is_valid = await client.webhooks.verify_signature(
    raw_json_body=request_body,  # Сырые байты тела запроса
    signature_header=request.headers.get("X-Signature")  # Значение заголовка X-Signature
)

if is_valid:
    # Обработка достоверного вебхука
    print("Получен достоверный вебхук")
else:
    # Отклонение недостоверного вебхука
    print("Получен недостоверный вебхук")

# Дополнительно: получение публичного ключа напрямую (обычно не требуется)
public_key = await client.webhooks.get_public_key_pem()
```

## Конфигурация

Конструктор `WataClient` принимает следующие параметры:

| Параметр     | Тип     | Описание                                     | По умолчанию |
|--------------|---------|----------------------------------------------|--------------|
| base_url     | str     | Базовый URL API                             | -            |
| jwt_token    | str     | JWT-токен для аутентификации                | None         |
| timeout      | int     | Таймаут запроса в секундах                  | 30           |
| max_retries  | int     | Максимальное количество попыток повтора     | 3            |
| log_level    | int     | Уровень логирования (из модуля logging)     | INFO         |

## Многопоточность и параллелизм

Клиент WATA API разработан для безопасной работы в асинхронной среде:

- Каждый экземпляр клиента полностью независим от других экземпляров
- HTTP-сессии не разделяются между экземплярами
- Используются асинхронные блокировки для предотвращения состояния гонки при работе с сессиями
- Вы можете создавать столько экземпляров, сколько требуется для ваших задач
- Каждый экземпляр может иметь свою собственную конфигурацию

## Обработка ошибок

Клиент предоставляет комплексную иерархию исключений:

- `ApiError` - Базовое исключение для всех ошибок API
  - `ApiConnectionError` - Ошибки соединения
    - `ApiTimeoutError` - Тайм-аут запроса
  - `ApiAuthError` - Ошибка аутентификации
  - `ApiForbiddenError` - Доступ запрещен
  - `ApiResourceNotFoundError` - Ресурс не найден
  - `ApiValidationError` - Неверные параметры запроса
  - `ApiServerError` - Серверные ошибки
    - `ApiServiceUnavailableError` - Сервис временно недоступен
  - `ApiParsingError` - Ошибка парсинга ответа API

## Разработка

### Предварительные требования

- Python 3.7+
- uv

### Настройка среды разработки

```bash
# Клонировать репозиторий
git clone <адрес-репозитория>
cd wataClient

# Установка зависимостей разработки с uv
uv pip install -e ".[dev]"

# Запуск примера
uv run python example.py
```

## Сборка и публикация

```bash
# Сборка пакета
uv build

# Публикация в PyPI
uv run python -m twine upload dist/*
```

## Лицензия

Этот проект лицензирован в соответствии с лицензией MIT - подробности см. в файле LICENSE.
