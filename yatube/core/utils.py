from django.conf import settings
from django.core.paginator import Paginator

# Колчичество постов на страницу
COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR


# Паджинация
def get_pages(request, posts):
    paginator = Paginator(posts, COUNT_PAGES)
    page_number = request.GET.get('page')

    # Возвращаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)
