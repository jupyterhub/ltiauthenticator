import re
from unittest.mock import Mock

import pytest

from tornado.web import RequestHandler

from ltiauthenticator.utils import convert_request_to_dict
from ltiauthenticator.utils import email_to_username
from ltiauthenticator.utils import get_client_protocol
from ltiauthenticator.utils import normalize_string


def test_normalize_string_return_false_with_missing_name():
    """
    Ensure that an empty string returns a value error.
    """
    my_string = ""
    with pytest.raises(ValueError):
        normalize_string(my_string)


def test_normalize_string_with_long_name():
    """
    Assert that the normalized string is truncated to 25 characters.
    """
    my_string = "this_is_a_really_long_string_lets_add_some_more"
    normalized_my_string = normalize_string(my_string)

    assert len(normalized_my_string) <= 25


def test_normalize_string_with_special_characters():
    """
    Assert that the string is correctly normalized when it includes special characters.
    """
    my_string = "#$%_this_is_a_string"
    normalized_my_string = normalize_string(my_string)
    regex = re.compile("[@!#$%^&*()<>?/\\|}{~:]")

    assert regex.search(normalized_my_string) is None


def test_normalize_string_with_first_letter_as_alphanumeric():
    """
    Assert that the string is correctly normalized to remove strings that begin with a special character.
    """
    my_string = "___this_is_a_string"
    normalized_my_string = normalize_string(my_string)
    regex = re.compile("_.-")
    first_character = normalized_my_string[0]
    assert first_character != regex.search(normalized_my_string)


def test_get_protocol_with_more_than_one_value():
    """
    Assert that the first (left-most) protocol value is correctly fetched from the x-forwarded-header.
    """
    handler = Mock(
        spec=RequestHandler,
        request=Mock(
            headers={"x-forwarded-proto": "https,http,http"},
            protocol="https",
        ),
    )
    expected = "https"
    protocol = get_client_protocol(handler)

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


def test_email_to_username_retrieves_only_username_part_before_at_symbol():
    """
    Ensure we get the user name from the string before the email's @ character.
    """
    email = "user1@example.com"

    # act
    result = email_to_username(email)
    assert result == "user1"


def test_email_to_username_converts_username_in_lowecase():
    """
    Assert that the user name is lower case when receiving upper case characters in an email.
    """
    email = "USER_name1@example.com"

    # act
    result = email_to_username(email)
    assert result == "user_name1"


def test_email_to_username_retrieves_only_first_part_before_plus_symbol():
    """
    Ensure we get the user name from the string before the email's + character.
    """
    email = "user+name@example.com"

    # act
    result = email_to_username(email)
    assert result == "user"
