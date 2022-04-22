"""
Приложение users отвечает за работу с пользователем:
регистрация, авторизация, восстановление пароля.
"""
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    """Класс, отвечающий за работу регистрации."""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
