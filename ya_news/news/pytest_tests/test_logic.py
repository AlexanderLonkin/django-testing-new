from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cannot_create_comment(
    client, news_url, news_login_url, form_data, db
):
    """Анонимный POST не создаёт комментарий."""
    response = client.post(news_url, data=form_data)

    assertRedirects(
        response,
        news_login_url,
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert Comment.objects.count() == 0


def test_authorized_user_creates_one_comment(
    author, author_client, news, news_url, comments_url, form_data, db
):
    """Авторизованный пользователь создаёт один комментарий."""
    response = author_client.post(news_url, data=form_data)

    assertRedirects(
        response,
        comments_url,
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
    author_client, news_url, db, bad_word
):
    """Комментарий со стоп-словом не сохраняется."""
    response = author_client.post(
        news_url,
        data={'text': f'Ты {bad_word}!'},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, edit_url, comments_url, form_data
):
    """Автор меняет текст своего комментария."""
    response = author_client.post(edit_url, data=form_data)

    edited_comment = Comment.objects.get(pk=comment.pk)
    assertRedirects(
        response,
        comments_url,
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert edited_comment.text == form_data['text']
    assert edited_comment.author == comment.author
    assert edited_comment.news == comment.news


def test_author_can_delete_comment(
    author_client, delete_url, comments_url
):
    """Автор удаляет свой комментарий."""
    response = author_client.post(delete_url)

    assertRedirects(
        response,
        comments_url,
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )
    assert Comment.objects.count() == 0


def test_other_user_cannot_edit_comment(
    reader_client, comment, edit_url, form_data
):
    """Другой пользователь не меняет чужой комментарий."""
    response = reader_client.post(edit_url, data=form_data)

    comment_after_request = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment_after_request.text == comment.text
    assert comment_after_request.author == comment.author
    assert comment_after_request.news == comment.news


def test_other_user_cannot_delete_comment(
    reader_client, comment, delete_url
):
    """Другой пользователь не удаляет чужой комментарий."""
    response = reader_client.post(delete_url)

    comment_after_request = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment_after_request.text == comment.text
    assert comment_after_request.author == comment.author
    assert comment_after_request.news == comment.news
