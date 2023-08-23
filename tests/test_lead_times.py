import pytest


from vans_bot.vans_lead_times import VansLeadTimeMonitor


@pytest.fixture
def lead_time_monitor():
    return VansLeadTimeMonitor()


@pytest.fixture
def lead_time_page():
    with open("tests/data/vans_lead_times.html", "rb") as f:
        return f.read()


def test_get_price_update(
    lead_time_monitor: VansLeadTimeMonitor, lead_time_page: bytes
):
    assert (
        lead_time_monitor.get_current_price_update(lead_time_page)
        == "March 6, 2023, 3:00 pm, Pacific Time"
    )


def test_get_lead_time_update(
    lead_time_monitor: VansLeadTimeMonitor, lead_time_page: bytes
):
    assert (
        lead_time_monitor.get_current_lead_time_update(lead_time_page) == "July 6, 2023"
    )


def test_page_structure_changed(lead_time_monitor: VansLeadTimeMonitor):
    with pytest.raises(ValueError):
        lead_time_monitor.get_current_price_update(b"")
    with pytest.raises(ValueError):
        lead_time_monitor.get_current_lead_time_update(b"")

    lead_time_monitor.get_current_lead_time_page = (  # type: ignore[method-assign]
        lambda: b""
    )
    assert len(lead_time_monitor.check_for_messages()) == 1
    assert not lead_time_monitor.continue_checking
    assert lead_time_monitor.check_for_messages() == []


def test_check_for_messages(
    lead_time_monitor: VansLeadTimeMonitor, lead_time_page: bytes
):
    lead_time_monitor.price_update = "January 1, 1970"
    lead_time_monitor.get_current_lead_time_page = (  # type: ignore[method-assign]
        lambda: lead_time_page
    )
    assert lead_time_monitor.check_for_messages() == [
        (
            "Van's has updated their <https://www.vansaircraft.com/order-a-kit/"
            "kit-prices-and-lead-times/|kit prices and lead times>!"
        )
    ]

    assert lead_time_monitor.check_for_messages() == []
