"""
Приложение core отвечает за работу страниц,
при ошибках в запросах к страницам.
"""
from django.shortcuts import render


def page_not_found(request, exception):
    """Функция отвечающая за работу страницы с ошибкой 404."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Функция отвечающая за работу страницы с ошибкой 500."""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """Функция отвечающая за работу страницы с ошибкой 403."""
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    """Функция отвечающая за работу страницы с ошибкой 403."""
    return render(request, 'core/403csrf.html')
