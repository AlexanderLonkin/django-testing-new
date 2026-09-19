from http import HTTPStatus
import pytest
from django.contrib.auth import SESSION_KEY


@pytest.mark.parametrize('page', ('home', 'detail', 'login', 'signup'))
def test_public_pages_are_available(
    client, home_url, news_url, auth_urls, page
):
    urls = {
        'home': home_url,
        'detail': news_url,
        'login': auth_urls['login'],
        'signup': auth_urls['signup'],
    }

    response = client.get(urls[page])

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('page', ('edit', 'delete'))
def test_comment_pages_are_available_to_author(
    author_client, comment_urls, page
):
    response = author_client.get(comment_urls[page])

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('page', ('edit', 'delete'))
def test_other_user_cannot_open_comment_pages(
    reader_client, comment_urls, page
):
    response = reader_client.get(comment_urls[page])

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('page', ('edit', 'delete'))
def test_anonymous_user_is_redirected_to_login(
    client, comment_urls, auth_urls, page
):
    source_url = comment_urls[page]
    login_url = auth_urls['login']
    expected_url = f'{login_url}?next={source_url}'

    response = client.get(source_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_by_post_clears_session(author_client, auth_urls):
    assert SESSION_KEY in author_client.session

    response = author_client.post(auth_urls['logout'])

    assert response.status_code == HTTPStatus.OK
    assert SESSION_KEY not in author_client.session
