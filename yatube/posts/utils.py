"""Приложение posts отвечает за работу сайта."""
from django.core.paginator import Paginator

from yatube.settings import NUMBER_OF_RECORDS


def paginator(request, post_list):
    """Функция, в которой реализовано разбитие постов по страницам."""
    paginator = Paginator(post_list, NUMBER_OF_RECORDS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
