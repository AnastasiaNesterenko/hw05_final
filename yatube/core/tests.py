"""
Тест, написанный с помощью модуля unittest.
Проверяет корректную работу views.py.
"""
from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    """
    Класс проверяет возвращается ли верный статус при ошибке
    и та ли страница отображается.
    """
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response, 'core/404.html')
