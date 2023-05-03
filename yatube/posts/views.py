from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

# isort: off
from core.utils import get_pages
# isort: on
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


# Главная страница
@cache_page(20, key_prefix='index_page')
def index(request):
    """Получаем все посты и выводим используя паджинатор get_pages."""
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = get_pages(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с постами отфильрованными по группам
def group_posts(request, slug):
    """
    По полученной slug строке получаем название группы,
    через related_name 'posts' получаем все посты выбранной группы,
    выводим с паджинацией get_pages.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_obj = get_pages(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Страница профиля со списком постов
def profile(request, username):
    """
    По полученной строке забираем имя пользователя,
    через related_name 'posts' получаем все его посты,
    выводим с паджинацией get_pages.
    """
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group').all()
    page_obj = get_pages(request, posts)
    following = (request.user.is_authenticated
                 and
                 Follow.objects.filter(
                    author=author,
                    user=request.user).exists())

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


# Страница с выбранным постом
def post_detail(request, post_id):
    """
    Получаем пост по pk, через ForeignKey-author полученного поста
    возвращаем текст посата и общее количество постов автора.
    """
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    count_posts = post.author.posts.all().count()
    form = CommentForm()
    context = {
        'post': post,
        'count_posts': count_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


# Создание поста
@login_required
def post_create(request):
    """
    Если не POST, создаем пустую форму.

    Если POST, передаем данные в объект form, проверяем на валидность,
    создаем объект поста, заполняем у него абрибут author,
    сохраняем новый пост в БД.

    После сохранения пользователь перенапавляется на страницу своего профиля.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect(reverse('posts:profile',
                                args=[request.user.username]))
    context = {
        'form': form,
    }
    return render(request, "posts/create_post.html", context)


# Редактирование поста
@login_required
def post_edit(request, post_id):
    """
    По полученному post_id забираем пост из БД.
    Если не POST, добавляем в объект формы данные из
    запрошенного поста.
    is_edit - для корректной генерации кнопок и названий формы
    при использовании одного шаблона.
    post_id - в context для генерации ссылки на редактирование.

    Если POST и валидна, сохраняем в БД.
    Если POST и не валидна, возвращаем пользователю.

    После сохранения пользователь перенапавляется на страницу своего профиля.
    """
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect(reverse('posts:post_detail', args=[post_id]))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(reverse('posts:post_detail', args=[post_id]))
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post.id
    }
    return render(request, 'posts/create_post.html', context)


# Добавление коментария к посту
@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к посту."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Выводит список постов авторов, на которых подписан пользователь."""
    user = get_object_or_404(User, username=request.user)
    # Все подписки пользователя
    subscriptions = Follow.objects.filter(user=user)
    # ID авторов полученных подписок
    authors = [a_id.author.id for a_id in subscriptions]
    # Все посты авторов
    posts = Post.objects.filter(author_id__in=authors)
    page_obj = get_pages(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    follower = request.user

    follow_exist = Follow.objects.filter(
        author=author, user=follower
    ).exists()

    if not follow_exist and author != follower:
        new_follow = Follow(author=author, user=follower)
        new_follow.save()
    return redirect(
        reverse('posts:profile',
                args=[author.username])
    )


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = get_object_or_404(User, username=username)

    Follow.objects.filter(
        author=author, user=request.user
    ).delete()
    return redirect(
        reverse('posts:profile',
                args=[author.username])
    )
