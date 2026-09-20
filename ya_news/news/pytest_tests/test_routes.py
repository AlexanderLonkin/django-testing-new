from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture',
    ('home_url', 'news_url', 'login_url', 'signup_url'),
)
def test_public_pages_are_available(
    client, request, url_fixture, db
):
    """Публичные страницы открываются анонимному пользователю."""
    response = client.get(request.getfixturevalue(url_fixture))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_comment_pages_are_available_to_author(
    author_client, request, url_fixture
):
    """Автор открывает страницы изменения своего комментария."""
    response = author_client.get(request.getfixturevalue(url_fixture))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_other_user_cannot_open_comment_pages(
    reader_client, request, url_fixture
):
    """Чужие страницы изменения комментария отвечают 404."""
    response = reader_client.get(request.getfixturevalue(url_fixture))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_anonymous_user_is_redirected_to_login(
    client, request, login_url, url_fixture
):
    """Анонимный пользователь попадает на вход с параметром next."""
    source_url = request.getfixturevalue(url_fixture)

    response = client.get(source_url)

    assertRedirects(
        response,
        f'{login_url}?next={source_url}',
        status_code=HTTPStatus.FOUND,
        fetch_redirect_response=False,
    )


def test_logout_by_post_returns_ok(author_client, logout_url):
    """POST-запрос выхода возвращает успешный ответ."""
    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
