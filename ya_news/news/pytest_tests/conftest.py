from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model, db):
    """Создаёт автора комментария."""
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def reader(django_user_model, db):
    """Создаёт другого пользователя."""
    return django_user_model.objects.create_user(username='reader')


@pytest.fixture
def author_client(author, db):
    """Создаёт клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    """Создаёт клиент с авторизованным читателем."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    """Создаёт новость для проверки комментариев."""
    return News.objects.create(title='Новость', text='Текст новости')


@pytest.fixture
def comment(news, author, db):
    """Создаёт комментарий автора к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Исходный комментарий',
    )


@pytest.fixture
def news_set(db):
    """Создаёт новости сверх лимита главной страницы."""
    first_date = timezone.localdate()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {index}',
            text='Текст новости',
            date=first_date + timedelta(days=index),
        )


@pytest.fixture
def timed_comments(news, author, db):
    """Создаёт комментарии с разным временем публикации."""
    first_time = timezone.now()
    for index, minutes in enumerate((10, 0, 5)):
        item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        Comment.objects.filter(pk=item.pk).update(
            created=first_time + timedelta(minutes=minutes),
        )


@pytest.fixture
def form_data():
    """Возвращает данные формы комментария."""
    return {'text': 'Новый комментарий'}


@pytest.fixture
def home_url():
    """Возвращает адрес главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_url(news, db):
    """Возвращает адрес страницы новости."""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment, db):
    """Возвращает адрес редактирования комментария."""
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment, db):
    """Возвращает адрес удаления комментария."""
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    """Возвращает адрес страницы входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Возвращает адрес страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """Возвращает адрес выхода из аккаунта."""
    return reverse('users:logout')
