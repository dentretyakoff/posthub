from django.test import TestCase
from django.urls import reverse

from ..forms import CreationForm


class UsersSignupViewTest(TestCase):
    def test_users_signup_form_correct(self):
        """SignUp формируется с правильным контекстом."""
        response = self.client.get(reverse('users:signup'))
        self.assertIsInstance(response.context.get('form'), CreationForm)
