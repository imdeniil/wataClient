"""
Модуль для работы с вебхуками WATA, включая автоматическое управление публичным ключом.
"""
import base64
from typing import Dict, Any, Optional

from .base import BaseApiModule
# Импортируем необходимые классы из библиотеки cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.exceptions import InvalidSignature


class WebhooksModule(BaseApiModule):
    """
    Модуль для работы с вебхуками WATA.
    Автоматически управляет получением и кэшированием публичного ключа
    для проверки подписи.
    """

    def __init__(self, http_client):
        """
        Инициализация модуля вебхуков.

        Аргументы:
            http_client: Экземпляр HTTP-клиента
        """
        super().__init__(http_client)
        # Кэш для хранения публичного ключа в PEM формате
        self._cached_public_key_pem: Optional[str] = None
        self.logger.debug("WebhooksModule инициализирован.")


    async def get_public_key_pem(self) -> str:
        """
        Получение публичного ключа для проверки подписи вебхуков WATA из API.

        Этот метод предназначен в основном для внутреннего использования модулем
        для обновления кэша ключа. Если вам нужен ключ для других целей,
        вы можете вызвать его напрямую, но в большинстве случаев управление
        ключом автоматизировано методом verify_signature.

        Возвращает:
            Строка, содержащая публичный ключ в PEM формате.

        Вызывает исключение:
            ApiException: Если запрос к API завершился неудачей или ответ не содержит ключ.
            (Предполагается, что self.http.get поднимает такое исключение)
        """
        self.logger.info("Запрос публичного ключа для вебхуков из API...")
        try:
            # Используем self.http для выполнения GET запроса к эндпоинту /public-key
            # Ожидаем, что self.http.get возвращает разобранный JSON
            # Уточните эндпоинт, если он отличается от /public-key (напр., /h2h/public-key)
            response_data: Dict[str, Any] = await self.http.get("/public-key")

            # Согласно документации, ключ находится в поле 'value'
            public_key_pem = response_data.get("value")

            if not public_key_pem or not isinstance(public_key_pem, str):
                self.logger.error("Публичный ключ не найден или имеет неверный формат в ответе API")
                # Поднимаем исключение, так как получить ключ не удалось
                raise ValueError("Неверный формат ответа API: публичный ключ не найден")

            self.logger.info("Публичный ключ успешно получен из API.")
            return public_key_pem

        except Exception as e:
            self.logger.error(f"Ошибка при получении публичного ключа из API: {e}", exc_info=True)
            # Перебрасываем исключение
            raise

    async def verify_signature(
        self,
        raw_json_body: bytes,
        signature_header: str
    ) -> bool:
        """
        Проверяет цифровую подпись вебхука WATA, автоматически управляя публичным ключом.

        Этот метод автоматически получает и кэширует публичный ключ, если он отсутствует
        или не был получен ранее.

        Использует публичный ключ, алгоритм хеширования SHA512 и PKCS1v15 padding
        для проверки подлинности полученного вебхука на основе заголовка X-Signature.

        Аргументы:
            raw_json_body: Сырое (неизмененное) тело запроса вебхука в виде байтов.
                           Критически важно использовать именно сырые байты тела запроса,
                           без какой-либо предварительной обработки или переформатирования JSON.
                           Эту информацию вы получаете от вашего веб-сервера/фреймворка.
            signature_header: Значение заголовка 'X-Signature' из запроса вебхука.
                              Это base64-encoded строка подписи.
                              Эту информацию вы также получаете от вашего веб-сервера/фреймворка.

        Возвращает:
            True, если подпись верна и тело запроса соответствует подписи.
            False в противном случае (неверная подпись, ошибка декодирования,
            невозможность получить публичный ключ и т.п.).

        Пример использования в обработчике вебхука (псевдокод):
            ```python
            # Внутри обработчика POST запроса по URL вебхука:
            # async def handle_wata_webhook(request): # Пример сигнатуры для aiohttp
            #     # 1. Получить сырое тело запроса как байты
            #     try:
            #         raw_body = await request.read() # Или request.get_data(), request.body в других фреймворках
            #     except Exception as e:
            #         logging.error(f"Не удалось прочитать тело вебхука: {e}")
            #         return web.Response(status=400, text="Invalid request body")

            #     # 2. Получить значение заголовка X-Signature
            #     signature = request.headers.get("X-Signature")

            #     if not signature:
            #         logging.warning("Получен вебхук без заголовка X-Signature.")
            #         return web.Response(status=400, text="X-Signature header missing")

            #     # 3. Проверить подпись с использованием модуля
            #     is_valid = await webhook_module.verify_signature(
            #         raw_json_body=raw_body,
            #         signature_header=signature
        """
        self.logger.debug("Начало проверки подписи вебхука...")

        # 1. Получение публичного ключа (с кэшированием)
        if self._cached_public_key_pem is None:
            self.logger.info("Публичный ключ отсутствует в кэше, выполняю запрос к API...")
            try:
                # Вызываем метод для получения ключа из API и кэшируем его
                self._cached_public_key_pem = await self.get_public_key_pem()
                if self._cached_public_key_pem is None:
                     # get_public_key_pem должен поднять исключение в этом случае,
                     # но эта проверка добавляет надежности.
                     self.logger.error("Метод get_public_key_pem вернул None.")
                     return False
                self.logger.info("Публичный ключ успешно получен и закэширован.")
            except Exception as e:
                self.logger.error(f"Не удалось получить публичный ключ из API для верификации: {e}", exc_info=True)
                # Если не можем получить ключ, проверить подпись невозможно.
                return False

        # Теперь public_key_pem гарантированно содержит ключ (или мы уже вернули False)
        public_key_pem_to_use = self._cached_public_key_pem

        try:
            # 2. Загрузка публичного ключа из PEM строки
            # Ключ в PEM формате должен быть закодирован в байты для load_pem_public_key
            public_key = serialization.load_pem_public_key(
                public_key_pem_to_use.encode('utf-8')
            )

            # Убедимся, что загружен именно RSA публичный ключ
            if not isinstance(public_key, RSAPublicKey):
                 self.logger.error("Загруженный ключ из кэша не является RSA публичным ключом.")
                 # Возможно, стоит сбросить кэш self._cached_public_key_pem = None
                 # для попытки повторного получения в следующий раз.
                 return False

            self.logger.debug("Публичный ключ успешно загружен из кэша.")

            # 3. Декодирование подписи из base64
            try:
                signature_bytes = base64.b64decode(signature_header)
                self.logger.debug("Подпись успешно декодирована из base64.")
            except Exception as e:
                self.logger.error(f"Ошибка декодирования подписи base64: {e}")
                return False


            # 4. Проверка подписи
            # Используем метод verify ключа: он принимает байты подписи, байты данных, padding и алгоритм
            # Согласно документации, используется SHA512 и RSA. Стандартное padding для RSA-подписей с хешем - PKCS1v15.
            public_key.verify(
                signature_bytes,
                raw_json_body,
                padding.PKCS1v15(), # Тип padding - PKCS1v15
                hashes.SHA512()    # Алгоритм хеширования - SHA512
            )

            # Если метод verify не вызвал исключение InvalidSignature, подпись верна
            self.logger.info("Проверка подписи вебхука успешно пройдена.")
            return True

        except InvalidSignature:
            # Это ожидаемое исключение при неверной подписи
            self.logger.warning("Проверка подписи вебхука НЕ пройдена: Неверная подпись.")
            # В случае неверной подписи, возможно, стоит попробовать обновить ключ
            # на случай его ротации на стороне WATA. Сбросим кэш.
            self._cached_public_key_pem = None
            self.logger.debug("Кэшированный публичный ключ сброшен после неудачной проверки.")
            return False
        except Exception as e:
            # Ловим любые другие ошибки (например, проблемы с загрузкой ключа из кэша,
            # неверный формат ключа в кэше и т.п.)
            self.logger.error(f"Произошла ошибка при проверке подписи вебхука: {e}", exc_info=True)
            # В случае ошибки обработки, также можно сбросить кэш на всякий случай.
            self._cached_public_key_pem = None
            self.logger.debug("Кэшированный публичный ключ сброшен после ошибки обработки.")
            return False