import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

# Колчичество постов на страницу
COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR
# Временная папка для сохранения прикрепляемых файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователей и клиенты
        cls.user = User.objects.create_user(username='StasBasov')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем группу и посты
        cls.group = Group.objects.create(
            title='Тестовая группа-1',
            slug='test-slug-1',
            description='Тестовое описание-1',
        )
        # Изображение для прикрепления к постам
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='views.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        # Количество постов в БД
        cls.COUNT_POSTS = Post.objects.count()

        # Константы urls-адресов
        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_URL = reverse('posts:group_list',
                                kwargs={'slug': cls.group.slug})
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.INDEX_URL
        )
        post = response.context['page_obj'][0]
        self.validate_content(post, self.post)

    def test_posts_cache_index_page(self):
        """Кеш главной страницы работает корректно."""
        new_post = Post.objects.create(
            text='Пост для проверки кеша главной страницы.',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        # Формируем кеш
        response = self.guest_client.get(self.INDEX_URL)
        post = response.context['page_obj'][0]
        content_1 = response.content
        # Содержимое полей соответствует ожиданиям
        self.validate_content(post, new_post)

        # Удаляем пост
        Post.objects.first().delete()
        # После удаления поста контент одинаковый
        response = self.guest_client.get(self.INDEX_URL)
        content_2 = response.content
        self.assertEqual(content_1, content_2)

        # Очищаем кеш, контент разный
        cache.clear()
        response = self.guest_client.get(self.INDEX_URL)
        content_2 = response.content
        self.assertNotEqual(content_1, content_2)

    def test_posts_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.GROUP_URL
        )
        post = response.context['page_obj'][0]
        group_name = response.context['group']

        self.validate_content(post, self.post)
        self.assertEqual(group_name, self.group)

    def test_posts_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.PROFILE_URL
        )
        post = response.context['page_obj'][0]
        user_name = response.context['author']

        self.validate_content(post, self.post)
        self.assertEqual(user_name, self.user)

    def test_posts_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.POST_DETAIL_URL
        )
        post = response.context['post']
        count_posts = response.context['count_posts']

        self.validate_content(post, self.post)
        self.assertEqual(count_posts, self.COUNT_POSTS)

    def validate_content(self, post: Post, post_expected: Post) -> None:
        """Содержимое полей поста соответствует ожиданиям."""
        post_content = {
            post.text: post_expected.text,
            post.author: post_expected.author,
            post.group: post_expected.group,
            post.image: post_expected.image,
        }
        for value, expected in post_content.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_posts_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.POST_CREATE_URL
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # В форму переданны корректные типы полей
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.POST_EDIT_URL
        )
        # В форму переданны корректные типы полей
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        # Значения is_edit и количество постов соответствуют ожидаемым
        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('post_id'),
                         self.post.id)

        # Содержимое полей соответсвует ожиданиям
        fields_content = {
            'text': self.post.text,
            'group': self.group.id,
        }
        for value, expected in fields_content.items():
            with self.subTest(value=value):
                content = response.context.get('form').initial.get(value)
                self.assertEqual(content, expected)

    def test_posts_correct_add_post_to_pages(self):
        """Пост корретно добавлен на страницы index, group_list, profile."""
        pages = (
            self.INDEX_URL,
            self.GROUP_URL,
            self.PROFILE_URL,
        )
        post = self.post
        for page in pages:
            response_guest = self.guest_client.get(page)
            cache.clear()
            response_auth = self.authorized_client.get(page)
            self.assertIn(post, response_guest.context['page_obj'])
            self.assertIn(post, response_auth.context['page_obj'])

    def test_posts_correct_add_post_to_group(self):
        """Пост не попал в группу, для которой не предназначен."""
        group_1 = self.group
        group_2 = Group.objects.create(
            title='Тестовая группа-2',
            slug='test-slug-2',
            description='Тестовое описание-2',
        )
        count_posts_group_1 = Post.objects.filter(group=group_1).count()
        count_posts_group_2 = Post.objects.filter(group=group_2).count()
        self.assertEqual(count_posts_group_1, self.COUNT_POSTS)
        self.assertEqual(count_posts_group_2, 0)


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Количество создаваемых постов
        cls.COUNT_POSTS = 23
        # Создаем пользователя и клиенты
        cls.user = User.objects.create_user(username='StasBasov')
        cls.client = Client()

        # Создаем группу и посты
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        posts = [
            Post(text=f'Тестовый пост-номер-{i}',
                 author=cls.user,
                 group=cls.group,
                 ) for i in range(cls.COUNT_POSTS)
        ]
        Post.objects.bulk_create(posts)
        # Константы URL-адресов
        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_URL = reverse('posts:group_list',
                                kwargs={'slug': cls.group.slug})
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user])

    def test_posts_correct_pages_paginator(self):
        """Количество постов на странице."""
        urls = (
            self.INDEX_URL,
            self.GROUP_URL,
            self.PROFILE_URL,
        )
        for url in urls:
            pages = self.client.get(url).context.get('page_obj')
            num_last_page = pages.paginator.num_pages
            last_page = pages.paginator.page(num_last_page)
            # Количество постов на первой странице
            self.assertEqual(len(pages), COUNT_PAGES)
            # Количество постов на последней странице
            self.assertEqual(len(last_page), self.COUNT_POSTS % COUNT_PAGES)


class PostFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователей и клиенты
        cls.user = User.objects.create_user(username='StasBasov')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Подписчик
        cls.follower = User.objects.create_user(username='follower')
        cls.auth_follower = Client()
        cls.auth_follower.force_login(cls.follower)

        # Неподписчик
        cls.unfollower = User.objects.create_user(username='unfollower')
        cls.auth_unfollower = Client()
        cls.auth_unfollower.force_login(cls.unfollower)

        # Константы URL-адресов
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user])
        cls.PROFILE_FOLLOW_URL = reverse('posts:profile_follow',
                                         args=[cls.user])
        cls.PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow',
                                           args=[cls.user])
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')

    def test_posts_auth_user_correct_follow(self):
        """Авторизованный пользователь может подписаться."""
        # Количество подписок в БД
        count_subs = Follow.objects.count()

        self.auth_follower.get(self.PROFILE_FOLLOW_URL)
        exists_sub = Follow.objects.first()

        # Подписка соответсвует ожиданиям
        self.assertEqual(exists_sub.author, self.user)
        self.assertEqual(exists_sub.user, self.follower)

        # Количество подписок увеличилось на 1
        self.assertEqual(Follow.objects.count(), count_subs + 1)

    def test_posts_auth_user_correct_unfollow(self):
        """Авторизованный пользователь может отписаться."""
        # Количество подписок в БД
        count_subs = Follow.objects.count()
        Follow.objects.create(
            author=self.user,
            user=self.follower,
        )
        self.auth_follower.get(self.PROFILE_UNFOLLOW_URL)
        # Подписка удалилась
        self.assertEqual(Follow.objects.all().count(),
                         count_subs,
                         'Количество подписок больше 0, '
                         'проверьте вью-функцию profile_unfollow')

    def test_posts_new_post_appears_correctly_in_favorites(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан."""
        # Количество подписок в БД
        count_subs = Follow.objects.count()
        # Подписываемся на автора
        Follow.objects.create(
            author=self.user,
            user=self.follower
        )
        # Автор создает новыый пост
        new_post = Post.objects.create(
            text='Тестовый пост для Избранного',
            author=self.user,
        )
        # Проверяем ленту подписчика
        response = self.auth_follower.get(self.FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context['page_obj']),
                         count_subs + 1,
                         'В избранном подписчика не появился новый пост.')

        post = response.context['page_obj'][0]
        self.assertEqual(post.text, new_post.text)
        self.assertEqual(post.author, new_post.author)

    def test_posts_new_post_not_appears_in_favorites(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан."""
        # Количество подписок в БД
        count_subs = Follow.objects.count()
        # Подписываемся на автора
        Follow.objects.create(
            author=self.user,
            user=self.follower
        )
        # Автор создает новыый пост
        Post.objects.create(
            text='Тестовый пост для Избранного',
            author=self.user,
        )
        # Проверяем ленту неподписчика
        response = self.auth_unfollower.get(self.FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context['page_obj']),
                         count_subs,
                         'Колчичество постов в избранном неподписчика '
                         'больше 0, проверьте вью-функцию profile_unfollow.')
