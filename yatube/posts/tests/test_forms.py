import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

# Временная папка для сохранения прикрепляемых файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя и клиенты
        cls.user_1 = User.objects.create_user(username='HasNoName')
        cls.user_2 = User.objects.create_user(username='NotAuthor')
        cls.auth_client_1 = Client()
        cls.auth_client_2 = Client()
        cls.auth_client_1.force_login(cls.user_1)
        cls.auth_client_2.force_login(cls.user_2)

        # Создаем группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создаем пост
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user_1,
        )
        cls.POST_COUNT = Post.objects.count()
        # Константы urls-адресов
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user_1])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.AUTH_URL = reverse('users:login')

        # Изображение для прикрепления к постам
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_create_form_correct(self):
        """Валидная форма создает запись в Post."""
        uploaded = SimpleUploadedFile(
            name='post_create_form.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст create_form',
            'group': self.group.id,
            'image': uploaded,
        }
        # Создаем пост
        response = self.auth_client_1.post(
            self.POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        # После успешного создания редирект на страницу профиля
        self.assertRedirects(response, self.PROFILE_URL)
        # Количество постов увеличилось
        self.assertEqual(Post.objects.count(), self.POST_COUNT + 1)
        # Пост с новым содержимым есть в базе
        self.post_exists(
            form_data.get('text'),
            f'posts/{uploaded.name}',
        )

    def test_posts_edit_form_author_correct(self):
        """Валидная форма для автора изменяет запись в Post."""
        uploaded = SimpleUploadedFile(
            name='post_edit_form.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        # Отредактированные данные для формы
        form_data = {
            'text': 'Тестовый текст edit_form_author',
            'group': self.group.id,
            'image': uploaded,
        }
        # Редактируем пост
        response = self.auth_client_1.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        # Произошел редирект на детали поста
        self.assertRedirects(response, self.POST_DETAIL_URL)
        # Количество постов не изменилось
        self.assertEqual(Post.objects.count(), self.POST_COUNT)
        # Отредактированная запись содержит корректные данные
        self.post_exists(
            form_data.get('text'),
            f'posts/{uploaded.name}'
        )

    def test_posts_edit_form_not_author_redirect(self):
        """Неавтора поста перенаправит на post_detail."""
        # Данные для формы
        form_data = {
            'text': 'Тестовый текст edit_form_not_author',
            'group': self.group.id,
        }
        # Редактируем пост
        response = self.auth_client_2.post(
            self.POST_EDIT_URL,
            data=form_data,
        )
        # Произошел редирект
        self.assertRedirects(response, self.POST_DETAIL_URL)
        # Количество постов не изменилось
        self.assertEqual(Post.objects.count(), self.POST_COUNT)
        # Содержимое поста не изменилось
        self.post_exists(self.post.text)

    def post_exists(self, text: str, img_name: str = '') -> None:
        """Пост существует в БД."""
        last_post = Post.objects.first()
        data = {
            last_post.text: text,
            last_post.group: self.group,
            last_post.author: self.user_1,
            last_post.image.name: img_name,
        }
        for value, expected in data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_posts_edit_form_anonymous_redirect(self):
        """
        Редактирование поста - анонимного пользователя
        редиректит на авторизацию
        """
        response = Client().get(
            self.POST_EDIT_URL,
            follow=True
        )
        # Произошел редирект
        self.assertRedirects(
            response,
            f'{self.AUTH_URL}?next={self.POST_EDIT_URL}')


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user_1 = User.objects.create_user(username='HasNoName')
        cls.auth_client_1 = Client()
        cls.auth_client_1.force_login(cls.user_1)
        # Создаем пост
        cls.post = Post.objects.create(
            text='Пост для теста комментария',
            author=cls.user_1,
        )
        # Создаем комментарий
        cls.comment = Comment(
            text=f'Тестовый комментарий к посту {cls.post.id}',
            post=cls.post,
            author=cls.user_1,
        )
        # Константы urls-адресов
        cls.COMMENT_CREATE_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id]
        )
        cls.AUTH_URL = reverse('users:login')

    def test_posts_create_comment_anonymous_redirect(self):
        """"
        Создание комментария - анонимного пользователя
        перенаправит на авторизацию.
        """
        count_comments = Comment.objects.all().count()
        form_data = {
            'text': f'Тестовый комментарий к посту {self.post.id}',
        }
        response = Client().post(
            self.COMMENT_CREATE_URL,
            data=form_data,
            follow=True
        )
        # Произошел редирект
        self.assertRedirects(
            response,
            f'{self.AUTH_URL}?next={self.COMMENT_CREATE_URL}')
        # Количесвто постов не изменилось
        self.assertEqual(Comment.objects.all().count(), count_comments)

    def test_posts_create_comment_form_correct(self):
        """Валидная форма создает комментарий."""
        # Получаем количество комментариев
        count_comments = Comment.objects.filter(post=self.post).count()
        # Создаем комментарий
        response = self.auth_client_1.post(
            self.COMMENT_CREATE_URL,
            data={'text': self.comment.text},
            follow=True
        )
        new_comment = response.context.get('comments')[0]
        comment_content = {
            new_comment.text: self.comment.text,
            new_comment.post: self.comment.post,
            new_comment.author: self.comment.author,

        }
        # Количество комментариев поста увеличилось на 1
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         count_comments + 1)
        # Комментарий есть на стринцие поста и соответсвует ожиданиям
        for value, expected in comment_content.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
