"""
Пакет модулей WATA API.
"""
from .links import LinksModule
from .payments import PaymentsModule
from .transactions import TransactionsModule
from .webhooks import WebhooksModule

__all__ = ["LinksModule", "PaymentsModule", "TransactionsModule", "WebhooksModule"]
