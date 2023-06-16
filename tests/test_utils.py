from unittest.mock import Mock

from ltiauthenticator.utils import convert_request_to_dict, get_browser_protocol


def test_get_protocol_with_more_than_one_value():
    """
    Assert that the first (left-most) protocol value is correctly fetched from the x-forwarded-header.
    """
    request = Mock(
        headers={"X-Forwarded-Proto": "https,http,http"},
        protocol="http",
    )
    expected = "https"
    protocol = get_browser_protocol(request)

    assert expected == protocol


def test_convert_request_arguments_with_encoded_items_to_dict():
    """
    Assert that a dict of k/v's is correctly created when receiving encoded values.
    """
    arguments = {
        "key1": [b"value1"],
        "key2": [b"value2"],
        "key3": [b"value3"],
    }
    expected = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    result = convert_request_to_dict(arguments)

    assert expected == result
