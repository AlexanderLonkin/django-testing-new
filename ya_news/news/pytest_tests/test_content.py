from news.forms import CommentForm


def test_home_page_has_ten_news(client, eleven_news, home_url):
    response = client.get(home_url)

    assert len(eleven_news) == 11
    assert len(response.context['object_list']) == 10


def test_news_are_sorted_newest_first(client, eleven_news, home_url):
    expected_dates = sorted(
        (item.date for item in eleven_news), reverse=True
    )[:10]

    response = client.get(home_url)

    dates = [item.date for item in response.context['object_list']]
    assert dates == expected_dates


def test_comments_are_sorted_oldest_first(
    client, timed_comments, news_url
):
    expected_times = sorted(item.created for item in timed_comments)

    response = client.get(news_url)

    comments = response.context['news'].comment_set.all()
    assert [item.created for item in comments] == expected_times


def test_anonymous_user_has_no_comment_form(client, news_url):
    response = client.get(news_url)

    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, news_url):
    response = author_client.get(news_url)

    assert isinstance(response.context['form'], CommentForm)
