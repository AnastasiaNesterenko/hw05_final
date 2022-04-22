"""
Приложение users отвечает за работу с пользователем:
регистрация, авторизация, восстановление пароля.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Регистрация приложения users."""
    name = 'users'
