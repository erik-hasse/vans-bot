from vans_bot.url_changed import URLChanged


def test_check_for_messages():
    page_monitor = URLChanged(url="https://example.com", page_name="Example Page")
    assert page_monitor.check_for_messages() == []
    old_hash = page_monitor.current_hash

    page_monitor.current_hash = 123
    assert page_monitor.check_for_messages() == [
        "Van's has changed <https://example.com|Example Page>!"
    ]
    assert page_monitor.current_hash == old_hash
