from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = '111'

    def test_posts_create_form_correct(self):
        """Пользователь зарегистрирован корректно."""
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'ivan',
            'email': 'ivan@ivanov.ru',
            'password1': 'Agft12361',
            'password2': 'Agft12361',
        }
        response = UserFormTests.client.post(
            reverse('users:signup'),
            data=form_data,
        )
        # Проверяем редирект после создания
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)
        # Проверяем, что пользовтел успешно создан
        self.assertTrue(
            User.objects.filter(
                username=form_data['username']
            )
        )
