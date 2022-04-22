"""
Приложение core отвечает за работу страниц,
при ошибках в запросах к страницам.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Регистрация приложения about."""
    name = 'core'
