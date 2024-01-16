import logging
from collections import defaultdict

import bs4  # type: ignore[import]
import requests

from vans_bot.base import BaseChecker

logger = logging.getLogger(__name__)


class VansLcpFaqMonitor(BaseChecker):
    def __init__(self):
        page = self.get_current_faq_page()
        self.questions = self.parse_questions(page)
        self.continue_checking = True

    def get_current_faq_page(self) -> bytes:
        resp = requests.get("https://www.vansaircraft.com/laser-cutting-customer-qa/")
        return resp.content

    def parse_questions(self, page: bytes) -> dict[str, str]:
        soup = bs4.BeautifulSoup(page, features="html.parser")
        qs = defaultdict(list)
        curr_q = ""
        for x in soup.find("div", class_="post-single__content").children:
            if x.text.startswith("Q:"):
                curr_q = x.text[3:]
            elif curr_q and x.text.strip():
                qs[curr_q].append(x.text.strip())

        return {k: "\n".join(v) for k, v in qs.items()}

    def get_question_changes(
        self, old: dict[str, str], new: dict[str, str]
    ) -> tuple[set[str], set[str], set[str]]:
        new_questions = set(new.keys()) - set(old.keys())
        changed_questions = {
            q for q in set(new.keys()) & set(old.keys()) if new[q] != old[q]
        }
        removed_questions = set(old.keys()) - set(new.keys())
        return new_questions, changed_questions, removed_questions

    def check_for_messages(self) -> list[str]:
        if not self.continue_checking:
            return []
        page = self.get_current_faq_page()
        try:
            questions = self.parse_questions(page)
        except Exception as e:
            logger.exception(e)
            self.continue_checking = False
            return [
                "Van's has changed the <https://www.vansaircraft.com/"
                "laser-cutting-customer-qa/|laser cutting Q&A> page!"
            ]
        if len(questions) == 0:
            self.continue_checking = False
            return [
                "Van's has changed the <https://www.vansaircraft.com/"
                "laser-cutting-customer-qa/|laser cutting Q&A> page!"
            ]

        if questions != self.questions:
            (
                new_questions,
                changed_questions,
                removed_questions,
            ) = self.get_question_changes(self.questions, questions)
            message = (
                "Van's has updated the <https://www.vansaircraft.com/"
                "laser-cutting-customer-qa/|laser cutting Q&A> page!"
            )
            for w, d in [
                ("added", new_questions),
                ("changed", changed_questions),
                ("removed", removed_questions),
            ]:
                if d:
                    message += f"\n\nThe following questions have been {w}:\n"
                    message += "\n".join(f"- {q}" for q in d)
            self.questions = questions
            return [message]
        return []
