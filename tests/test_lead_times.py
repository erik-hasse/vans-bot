import pytest


from vans_bot.vans_lead_times import VansLeadTimeMonitor


@pytest.fixture
def lead_time_monitor():
    return VansLeadTimeMonitor()


@pytest.fixture
def lead_time_page():
    with open("tests/data/vans_lead_times.html", "rb") as f:
        return f.read()


def test_page_structure_changed(lead_time_monitor: VansLeadTimeMonitor):
    with pytest.raises(ValueError):
        lead_time_monitor.parse_sections(b"")

    lead_time_monitor.get_current_lead_time_page = (  # type: ignore[method-assign]
        lambda: b""
    )
    assert len(lead_time_monitor.check_for_messages()) == 1
    assert not lead_time_monitor.continue_checking
    assert lead_time_monitor.check_for_messages() == []


def test_parse_sections(lead_time_monitor: VansLeadTimeMonitor, lead_time_page: bytes):
    sections = lead_time_monitor.parse_sections(lead_time_page)
    assert len(sections) == 3
    assert all(len(section) > 0 for section in sections.values())


def test_check_for_messages(
    lead_time_monitor: VansLeadTimeMonitor, lead_time_page: bytes
):
    lead_time_monitor.get_current_lead_time_page = (  # type: ignore[method-assign]
        lambda: lead_time_page
    )
    lead_time_monitor.sections = lead_time_monitor.parse_sections(lead_time_page)
    lead_time_monitor.sections["RV Kit Prices"] = "foo"
    assert lead_time_monitor.check_for_messages() == [
        (
            "Van's has updated the <https://www.vansaircraft.com/order-a-kit/"
            "kit-prices-and-lead-times/|kit prices and lead times> page!\n\n"
            "The following sections have changed:\n"
            "- RV Kit Prices"
        )
    ]

    assert lead_time_monitor.check_for_messages() == []
