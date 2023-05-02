from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Test')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_users_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_urls_allow_any_users(self):
        """URL-адрес доступен всем."""
        urls = [
            reverse('users:signup'),
            reverse('users:login'),
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_urls_allow_authorized_users(self):
        """URL-адрес доступен авторизованным пользователям."""
        urls = [
            reverse('users:password_change'),
            reverse('users:password_change_done'),
            reverse('users:logout'),
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
