import logging

import bs4
import requests

from vans_bot.base import BaseChecker
from vans_bot.page_diff import get_changes


logger = logging.getLogger(__name__)


class VansLeadTimeMonitor(BaseChecker):
    def __init__(self, page: str | None = None):
        if page is None:
            self.page = self.get_current_lead_time_page()
        else:
            self.page = self.get_main_content(page)

    @classmethod
    def get_current_lead_time_page(cls) -> str:
        resp = requests.get(
            "https://www.vansaircraft.com/order-a-kit/kit-prices-and-lead-times/"
        )
        resp.raise_for_status()
        return cls.get_main_content(resp.content)

    @classmethod
    def get_main_content(cls, page: str | bytes) -> str:
        soup = bs4.BeautifulSoup(page, features="html.parser")
        return soup.find(class_="post-single").decode()

    def check_for_messages(self) -> list[str]:
        page = self.get_current_lead_time_page()
        if page != self.page:
            change_summary = get_changes(self.page, page)
            return [
                "Van's has updated the <https://www.vansaircraft.com/order-a-kit/"
                "kit-prices-and-lead-times/|kit prices and lead times> page!\n\n"
                f"🤖 Change summary:\n{change_summary}"
            ]
        return []
