from django.conf import settings

from news.forms import CommentForm


def test_home_page_has_ten_news(client, news_set, home_url):
    """Главная страница показывает не больше десяти новостей."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    assert response.context['object_list'].count() == (
        settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_are_sorted_newest_first(client, news_set, home_url):
    """Новости на главной идут от новых к старым."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    dates = [item.date for item in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_comments_are_sorted_oldest_first(
    client, timed_comments, news_url
):
    """Комментарии к новости идут от старых к новым."""
    response = client.get(news_url)

    assert 'news' in response.context
    times = [
        item.created
        for item in response.context['news'].comment_set.all()
    ]
    assert times == sorted(times)


def test_anonymous_user_has_no_comment_form(client, news_url):
    """Анонимный пользователь не получает форму комментария."""
    response = client.get(news_url)

    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, news_url):
    """Авторизованный пользователь получает форму комментария."""
    response = author_client.get(news_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
