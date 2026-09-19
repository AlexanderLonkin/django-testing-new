from datetime import date, datetime, timedelta, timezone

import pytest
from django.test import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create_user(username='reader')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Новость', text='Текст новости')


@pytest.fixture
def comment(news, author, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Исходный комментарий',
    )


@pytest.fixture
def eleven_news(db):
    first_date = date(2024, 1, 1)
    return [
        News.objects.create(
            title=f'Новость {index}',
            text='Текст новости',
            date=first_date + timedelta(days=index),
        )
        for index in range(11)
    ]


@pytest.fixture
def timed_comments(news, author, db):
    first_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
    comments = []
    for index, minutes in enumerate((10, 0, 5)):
        item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        Comment.objects.filter(pk=item.pk).update(
            created=first_time + timedelta(minutes=minutes),
        )
        item.refresh_from_db()
        comments.append(item)
    return comments


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_url(news, db):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def comment_urls(comment, db):
    return {
        'edit': reverse('news:edit', args=(comment.pk,)),
        'delete': reverse('news:delete', args=(comment.pk,)),
    }


@pytest.fixture
def auth_urls():
    return {
        'login': reverse('users:login'),
        'signup': reverse('users:signup'),
        'logout': reverse('users:logout'),
    }
