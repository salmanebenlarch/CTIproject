from app.utils.indicators import classify_indicator


def test_classify_url() -> None:
    assert classify_indicator('https://example.com') == 'url'


def test_classify_ip() -> None:
    assert classify_indicator('8.8.8.8') == 'ip'


def test_classify_domain() -> None:
    assert classify_indicator('example.com') == 'domain'


def test_classify_hash() -> None:
    assert classify_indicator('44d88612fea8a8f36de82e1278abb02f') == 'hash'
