from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Главная страница обрабатывается вью-функцией index() из приложения Posts
    path('', include('posts.urls', namespace='posts')),

    # Встроенная админка
    path('admin/', admin.site.urls),

    # Кастомный модуль авторизации пользователей
    path('auth/', include('users.urls')),

    # Встроенный модуль авторизации пользователей
    path('auth/', include('django.contrib.auth.urls')),

    # О проекте
    path('about/', include('about.urls', namespace='about')),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
