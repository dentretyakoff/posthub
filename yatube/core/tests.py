from django.test import Client, TestCase


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGE_404_URL = '/unexisting_page/'
        cls.PAGE_404_TEMPL = 'core/404.html'

    def test_core_404_template(self):
        """Страница 404 отдает кастомный шаблон."""
        response = Client().get(self.PAGE_404_URL)
        self.assertTemplateUsed(response, self.PAGE_404_TEMPL)
