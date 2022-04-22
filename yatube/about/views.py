"""
Приложение about отвечает за страницы владельца сайта.
Включает в себя страницы об авторе и
страницу со списком использованных технологий.
"""
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс описывающий работу страницы "об авторе"."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """
    Класс описывающий работу страницы
    "об использованных технологиях".
    """
    template_name = 'about/tech.html'
