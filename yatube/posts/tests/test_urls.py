from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя и клиенты
        cls.user = User.objects.create_user(username='HasNoName')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем группу и пост
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост-123',
        )
        # Константы urls-адресов и шаблонов
        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_URL = reverse('posts:group_list',
                                kwargs={'slug': cls.group.slug})
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.UNEXISTING_PAGE = '/unexisting_page/'
        cls.AUTH_URL = reverse('users:login')
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')
        cls.PROFILE_FOLLOW_URL = reverse('posts:profile_follow',
                                         args=[cls.user])
        cls.PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow',
                                           args=[cls.user])

        cls.INDEX_TEMPL = 'posts/index.html'
        cls.GROUP_TEMPL = 'posts/group_list.html'
        cls.PROFILE_TEMPL = 'posts/profile.html'
        cls.POST_DETAIL_TEMPL = 'posts/post_detail.html'
        cls.POST_CREATE_TEMPL = 'posts/create_post.html'
        cls.POST_EDIT_TEMPL = 'posts/create_post.html'
        cls.FOLLOW_INDEX_TEMPL = 'posts/follow.html'

    def setUp(self):
        cache.clear()

    # Проверяем используемые шаблоны
    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.INDEX_URL: self.INDEX_TEMPL,
            self.GROUP_URL: self.GROUP_TEMPL,
            self.PROFILE_URL: self.PROFILE_TEMPL,
            self.POST_DETAIL_URL: self.POST_DETAIL_TEMPL,
            self.POST_CREATE_URL: self.POST_CREATE_TEMPL,
            self.POST_EDIT_URL: self.POST_EDIT_TEMPL,
            self.FOLLOW_INDEX_URL: self.FOLLOW_INDEX_TEMPL,
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_allow_any_users(self):
        """URL-адрес всем."""
        urls = [
            self.INDEX_URL,
            self.GROUP_URL,
            self.PROFILE_URL,
            self.POST_DETAIL_URL,
        ]
        # Проверка существующих страниц
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверка несуществующей страницы
        response = self.guest_client.get(self.UNEXISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_urls_allow_authorized_users_redirect_anonymous(self):
        """URL-адрес доступен только авторизованным пользователям,
        перенаправит анонимного пользователя на страницу логина."""
        url_names = [
            self.POST_CREATE_URL,
            self.POST_EDIT_URL,
            self.FOLLOW_INDEX_URL,
            self.PROFILE_FOLLOW_URL,
            self.PROFILE_UNFOLLOW_URL,
        ]
        # Авторизованный клиент получит код 200
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Неавторизованный клиент переадресует на авторизацию
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response,
                                     f'{self.AUTH_URL}?next={address}')
