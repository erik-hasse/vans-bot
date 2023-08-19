from datetime import datetime

import pytest

from vans_bot.vans_news import Article, VansNewsMonitor


@pytest.fixture
def article_1():
    return Article(
        id="post-1",
        title="Article 1",
        url="https://www.vansaircraft.com/news/article-1",
        timestamp=datetime.fromisoformat("2021-01-01T00:00:00"),
        content="Article 1 content",
    )


@pytest.fixture
def article_2():
    return Article(
        id="post-2",
        title="Article 2",
        url="https://www.vansaircraft.com/news/article-2",
        timestamp=datetime.fromisoformat("2021-01-02T00:00:00"),
        content="Article 2 content",
    )


@pytest.fixture
def article_1_content_changed():
    return Article(
        id="post-1",
        title="Article 1",
        url="https://www.vansaircraft.com/news/article-1",
        timestamp=datetime.fromisoformat("2021-01-01T00:00:00"),
        content="Article 1 content changed",
    )


@pytest.fixture
def monitor():
    return VansNewsMonitor()


def test_parse_news_page(monitor: VansNewsMonitor):
    with open("tests/data/vans_news.html", "rb") as f:
        content = f.read()
    articles = monitor.parse_news_page(content)
    assert len(articles) == 20
    assert all(isinstance(a, Article) for a in articles.values())
    assert all(
        a.url.startswith("https://www.vansaircraft.com") for a in articles.values()
    )


def test_find_new_articles(
    monitor: VansNewsMonitor, article_1: Article, article_2: Article
):
    old_articles = {article_1.id: article_1}
    updated_articles = {article_1.id: article_1, article_2.id: article_2}
    new_articles = monitor.find_new_articles(
        old_articles=old_articles, updated_articles=updated_articles
    )
    assert len(new_articles) == 1
    assert new_articles[0] == article_2

    new_articles = monitor.find_new_articles(
        old_articles=updated_articles, updated_articles=updated_articles
    )
    assert len(new_articles) == 0


def test_find_changed_articles(
    monitor: VansNewsMonitor, article_1: Article, article_1_content_changed: Article
):
    old_articles = {article_1.id: article_1}
    updated_articles = {article_1.id: article_1_content_changed}
    changed_articles = monitor.find_changed_articles(
        old_articles=old_articles, updated_articles=updated_articles
    )
    assert len(changed_articles) == 1
    assert changed_articles[0] == article_1_content_changed

    changed_articles = monitor.find_changed_articles(
        old_articles=updated_articles, updated_articles=updated_articles
    )
    assert len(changed_articles) == 0


def test_check_for_messages(
    monitor: VansNewsMonitor,
    article_1: Article,
    article_2: Article,
    article_1_content_changed: Article,
):
    monitor.current_articles = {article_1.id: article_1}
    monitor.get_current_articles = lambda: {  # type: ignore[method-assign]
        article_1_content_changed.id: article_1_content_changed
    }
    messages = monitor.check_for_messages()
    assert len(messages) == 1
    assert messages[0] == (
        f"Van's has changed an article <{article_1_content_changed.url}|"
        f"{article_1_content_changed.title}>!"
    )
    assert monitor.current_articles == {
        article_1_content_changed.id: article_1_content_changed
    }

    message = monitor.check_for_messages()
    assert len(message) == 0

    monitor.get_current_articles = lambda: {  # type: ignore[method-assign]
        article_1_content_changed.id: article_1_content_changed,
        article_2.id: article_2,
    }
    messages = monitor.check_for_messages()
    assert len(messages) == 1
    assert messages[0] == (
        f"Van's has posted a new article <{article_2.url}|{article_2.title}>!"
    )
