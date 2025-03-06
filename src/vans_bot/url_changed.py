import requests

from vans_bot.base import BaseChecker


class URLChanged(BaseChecker):
    def __init__(self, url: str, page_name: str):
        self.url = url
        self.page_name = page_name
        self.current_hash = self.get_current_content()

    def get_current_content(self) -> int:
        resp = requests.get(self.url)
        return hash(resp.content)

    def check_for_messages(self) -> list[str]:
        new_hash = self.get_current_content()
        if new_hash != self.current_hash:
            self.current_hash = new_hash
            return [f"Van's has changed <{self.url}|{self.page_name}>!"]
        return []
