from http import HTTPStatus
from urllib.parse import parse_qs, urlsplit

import pytest

from news.models import Comment


def test_anonymous_user_cannot_create_comment(
    client, news, news_url, auth_urls, db
):
    count_before = Comment.objects.count()

    response = client.post(news_url, data={'text': 'Новый комментарий'})

    redirect = urlsplit(response.url)
    assert response.status_code == HTTPStatus.FOUND
    assert redirect.path == auth_urls['login']
    assert parse_qs(redirect.query)['next'] == [news_url]
    assert Comment.objects.count() == count_before


def test_authorized_user_creates_one_comment(
    author, author_client, news, news_url, db
):
    text = 'Новый комментарий'
    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(news_url, data={'text': text})

    created = Comment.objects.exclude(pk__in=existing_ids)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_url}#comments'
    assert created.count() == 1
    saved = Comment.objects.get(pk=created.get().pk)
    assert saved.text == text
    assert saved.author == author
    assert saved.news == news


def test_comment_with_forbidden_word_is_not_saved(
    author_client, news_url, db
):
    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(
        news_url, data={'text': 'Ты редиска!'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'] == ['Не ругайтесь!']
    assert set(Comment.objects.values_list('pk', flat=True)) == existing_ids


def test_author_can_edit_comment(
    author_client, comment, comment_urls, news_url
):
    new_text = 'Изменённый комментарий'
    original_author = comment.author
    original_news = comment.news

    response = author_client.post(
        comment_urls['edit'], data={'text': new_text}
    )

    saved = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_url}#comments'
    assert saved.text == new_text
    assert saved.author == original_author
    assert saved.news == original_news


def test_author_can_delete_comment(
    author_client, comment, comment_urls, news_url
):
    comment_id = comment.pk
    count_before = Comment.objects.count()

    response = author_client.post(comment_urls['delete'])

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_url}#comments'
    assert not Comment.objects.filter(pk=comment_id).exists()
    assert Comment.objects.count() == count_before - 1


@pytest.mark.parametrize('page', ('edit', 'delete'))
def test_other_user_cannot_change_comment(
    reader_client, comment, comment_urls, page
):
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    count_before = Comment.objects.count()

    response = reader_client.post(
        comment_urls[page], data={'text': 'Чужое изменение'}
    )

    saved = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_before
    assert saved.text == original_text
    assert saved.author == original_author
    assert saved.news == original_news
