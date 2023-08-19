import re
from dataclasses import dataclass
from datetime import datetime

import bs4  # type: ignore[import]
import requests

from vans_bot.base import BaseChecker


@dataclass
class Article:
    id: str
    title: str
    url: str
    timestamp: datetime
    content: str


class VansNewsMonitor(BaseChecker):
    def __init__(self):
        self.current_articles = self.get_current_articles()

    def parse_article(self, article: bs4.Tag) -> Article:
        return Article(
            id=next(c for c in article["class"] if re.match(r"post-\d+", c)),
            title=article.find("h2").text,
            url=article.find("a")["href"],
            timestamp=datetime.fromisoformat(article.find("time")["datetime"]),
            content=article.find("div", class_="post-entry__summary").text,
        )

    def parse_news_page(self, content: bytes) -> dict[str, Article]:
        soup = bs4.BeautifulSoup(content, features="html.parser")
        articles = [
            self.parse_article(a) for a in soup.find_all("article", class_="post-entry")
        ]
        return {a.id: a for a in articles}

    def get_current_articles(self) -> dict[str, Article]:
        resp = requests.get("https://www.vansaircraft.com/news/")
        return self.parse_news_page(resp.content)

    def find_new_articles(
        self, old_articles: dict[str, Article], updated_articles: dict[str, Article]
    ) -> list[Article]:
        return sorted(
            [a for a in updated_articles.values() if a.id not in old_articles.keys()],
            key=lambda x: x.timestamp,
        )

    def find_changed_articles(
        self, old_articles: dict[str, Article], updated_articles: dict[str, Article]
    ) -> list[Article]:
        return sorted(
            [
                a
                for a in updated_articles.values()
                if a.id in old_articles.keys() and a != old_articles[a.id]
            ],
            key=lambda x: x.timestamp,
        )

    def check_for_messages(self) -> list[str]:
        new_articles = self.get_current_articles()
        messages = [
            f"Van's has posted a new article <{article.url}|{article.title}>!"
            for article in self.find_new_articles(
                old_articles=self.current_articles, updated_articles=new_articles
            )
        ] + [
            f"Van's has changed an article <{article.url}|{article.title}>!"
            for article in self.find_changed_articles(
                old_articles=self.current_articles, updated_articles=new_articles
            )
        ]

        self.current_articles = new_articles
        return messages
