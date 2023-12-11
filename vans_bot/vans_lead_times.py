import logging
import typing as t
from itertools import takewhile

import bs4  # type: ignore[import]
import requests

from vans_bot.base import BaseChecker

logger = logging.getLogger(__name__)


class VansLeadTimeMonitor(BaseChecker):
    def __init__(self):
        page = self.get_current_lead_time_page()
        self.sections = self.parse_sections(page)
        self.continue_checking = True

    def get_current_lead_time_page(self) -> bytes:
        resp = requests.get(
            "https://www.vansaircraft.com/order-a-kit/kit-prices-and-lead-times/"
        )
        return resp.content

    def parse_sections(self, page: bytes) -> dict[str, t.Any]:
        soup = bs4.BeautifulSoup(page, features="html.parser")
        headings = soup.find_all("h3")
        if len(headings) != 3 or len(set(h.parent for h in headings)) != 1:
            raise ValueError("Page structure has changed!")

        return {
            h.text.strip(" \n:"): list(
                takewhile(lambda h: h.name != "h3", h.next_siblings)
            )
            for h in headings
        }

    def check_for_messages(self) -> list[str]:
        if not self.continue_checking:
            return []
        page = self.get_current_lead_time_page()
        try:
            sections = self.parse_sections(page)
        except ValueError as e:
            logger.exception(e)
            self.continue_checking = False
            return [
                "Van's has changed the <https://www.vansaircraft.com/order-a-kit/"
                "kit-prices-and-lead-times/|kit prices and lead times> page!"
            ]
        if sections != self.sections:
            changed_sections = [
                name
                for name, section in sections.items()
                if section != self.sections.get(name)
            ]
            self.sections = sections
            return [
                "Van's has updated the <https://www.vansaircraft.com/order-a-kit/"
                "kit-prices-and-lead-times/|kit prices and lead times> page!"
                "The following sections have changed:\n"
                + "\n".join(f"* {name}" for name in changed_sections)
            ]
        return []
