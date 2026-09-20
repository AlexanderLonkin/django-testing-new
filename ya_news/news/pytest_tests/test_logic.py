from http import HTTPStatus

import pytest
from django.contrib.auth import SESSION_KEY
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS
from news.models import Comment


def test_logout_clears_session(author_client, logout_url):
    """После выхода пользователь отсутствует в сессии."""
    author_client.post(logout_url)

    assert SESSION_KEY not in author_client.session


def test_anonymous_user_cannot_create_comment(
    client, news_url, login_url, form_data, db
):
    """Анонимный POST не создаёт комментарий."""
    response = client.post(news_url, data=form_data)

    assertRedirects(
        response,
        f'{login_url}?next={news_url}',
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert Comment.objects.count() == 0


def test_authorized_user_creates_one_comment(
    author, author_client, news, news_url, form_data, db
):
    """Авторизованный пользователь создаёт один комментарий."""
    response = author_client.post(news_url, data=form_data)

    assertRedirects(
        response,
        f'{news_url}#comments',
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert Comment.objects.count() == 1
    created_comment = Comment.objects.get()
    assert created_comment.text == form_data['text']
    assert created_comment.author == author
    assert created_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_forbidden_word_is_not_saved(
    author_client, news_url, form_data, db, bad_word
):
    """Комментарий со стоп-словом не сохраняется."""
    form_data['text'] = f'Ты {bad_word}!'

    response = author_client.post(news_url, data=form_data)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assertFormError(response.context['form'], 'text', 'Не ругайтесь!')
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, edit_url, news_url, form_data
):
    """Автор меняет текст своего комментария."""
    form_data['text'] = 'Изменённый комментарий'

    response = author_client.post(edit_url, data=form_data)

    edited_comment = Comment.objects.get(pk=comment.pk)
    assertRedirects(
        response,
        f'{news_url}#comments',
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert edited_comment.text == form_data['text']
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news


def test_author_can_delete_comment(
    author_client, delete_url, news_url
):
    """Автор удаляет свой комментарий."""
    response = author_client.post(delete_url)

    assertRedirects(
        response,
        f'{news_url}#comments',
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_other_user_cannot_change_comment(
    reader_client, comment, form_data, request, url_fixture
):
    """Другой пользователь не меняет и не удаляет комментарий."""
    response = reader_client.post(
        request.getfixturevalue(url_fixture),
        data=form_data,
    )

    comment_after_request = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment_after_request.text == comment.text
    assert comment_after_request.author == comment.author
    assert comment_after_request.news == comment.news
