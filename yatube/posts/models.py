from core.models import CreatedModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

# Количество символов при вызове метода __str__ модели Post
COUNT_SYMBOLS = settings.COUNT_SYMBOLS_POST

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=(self.pk, ))

    def __str__(self):
        # выводим текст поста
        return self.text[:COUNT_SYMBOLS]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def get_absolute_url(self):
        return reverse('posts:group_list', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    def __str__(self):
        return self.text[:COUNT_SYMBOLS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.author}-{self.user}'
