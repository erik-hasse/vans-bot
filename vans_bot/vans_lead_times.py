import re

import requests

from vans_bot.base import BaseChecker


class VansLeadTimeMonitor(BaseChecker):
    def __init__(self):
        page = self.get_current_lead_time_page()
        self.price_update = self.get_current_price_update(page)
        self.lead_time_update = self.get_current_lead_time_update(page)
        self.continue_checking = True

    def get_current_lead_time_page(self) -> bytes:
        resp = requests.get(
            "https://www.vansaircraft.com/order-a-kit/kit-prices-and-lead-times/"
        )
        return resp.content

    def get_current_price_update(self, page: bytes) -> str:
        r = re.search(rb"<em>Kit prices effective: (.+)</em>", page)
        if r is None:
            raise ValueError("Could not find price update - the page has changed")
        return r.group(1).decode("utf-8")

    def get_current_lead_time_update(self, page: bytes) -> str:
        r = re.search(rb"<em>Estimated lead times effective: (.+)</em>", page)
        if r is None:
            raise ValueError("Could not find lead time update - the page has changed")
        return r.group(1).decode("utf-8")

    def check_for_messages(self) -> list[str]:
        if not self.continue_checking:
            return []
        page = self.get_current_lead_time_page()
        try:
            price_update = self.get_current_price_update(page)
            lead_time_update = self.get_current_lead_time_update(page)
        except ValueError:
            self.continue_checking = False
            return [
                "Van's has changed <https://www.vansaircraft.com/order-a-kit/"
                "kit-prices-and-lead-times/|kit prices and lead times>!"
            ]
        if (
            price_update != self.price_update
            or lead_time_update != self.lead_time_update
        ):
            self.price_update = price_update
            self.lead_time_update = lead_time_update
            return [
                "Van's has updated their <https://www.vansaircraft.com/order-a-kit/"
                "kit-prices-and-lead-times/|kit prices and lead times>!"
            ]
        return []
