import pytest

from vans_bot.vans_lcp_faq import VansLcpFaqMonitor


@pytest.fixture
def lcp_faq_monitor():
    return VansLcpFaqMonitor()


@pytest.fixture
def lcp_faq_page():
    with open("tests/data/lcp_faq.html", "rb") as f:
        return f.read()


def test_parse_page(lcp_faq_monitor: VansLcpFaqMonitor, lcp_faq_page: bytes):
    questions = lcp_faq_monitor.parse_questions(lcp_faq_page)
    assert len(questions) == 10
    assert all(len(q) > 0 for q in questions.values())


def test_questions_changed(lcp_faq_monitor: VansLcpFaqMonitor):
    old = {
        "a": "foo",
        "b": "bar",
        "c": "baz",
    }
    new = {
        "a": "foo",
        "b": "baz",
        "d": "qux",
    }
    new_qs, changed_qs, removed_qs = lcp_faq_monitor.get_question_changes(old, new)
    assert new_qs == {"d"}
    assert changed_qs == {"b"}
    assert removed_qs == {"c"}


def test_check_for_messages(lcp_faq_monitor: VansLcpFaqMonitor, lcp_faq_page: bytes):
    lcp_faq_monitor.get_current_faq_page = (  # type: ignore[method-assign]
        lambda: lcp_faq_page
    )
    lcp_faq_monitor.questions = lcp_faq_monitor.parse_questions(lcp_faq_page)
    # Set the old questions
    lcp_faq_monitor.questions["Why stop laser-cutting?"] = "foo"
    del lcp_faq_monitor.questions["When will I receive my replacement parts?"]
    lcp_faq_monitor.questions["bar"] = "baz"
    assert lcp_faq_monitor.check_for_messages() == [
        (
            "Van's has updated the <https://www.vansaircraft.com/"
            "laser-cutting-customer-qa/|laser cutting Q&A> page!\n\n"
            "The following questions have been added:\n"
            "- When will I receive my replacement parts?\n\n"
            "The following questions have been changed:\n"
            "- Why stop laser-cutting?\n\n"
            "The following questions have been removed:\n"
            "- bar"
        )
    ]

    assert lcp_faq_monitor.check_for_messages() == []
