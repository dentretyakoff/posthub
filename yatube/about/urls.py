from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    # Об авторе
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    # О проекте
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
