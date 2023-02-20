import json
from unittest.mock import Mock, patch

import pytest
from tornado.httputil import HTTPServerRequest
from tornado.web import HTTPError, RequestHandler

from ltiauthenticator.lti11.auth import LTI11Authenticator
from ltiauthenticator.lti11.validator import LTI11LaunchValidator

from .mocking import MockLTI11Authenticator


async def test_authenticator_uses_lti11validator(
    auth_args,
):
    """
    Ensure that we call the LTI11Validator from the LTI11Authenticator.
    """
    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ) as mock_validator:
        authenticator = MockLTI11Authenticator()
        authenticator.username_key = "custom_canvas_user_id"
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(
            method="POST",
            connection=Mock(),
        )
        handler.request = request

        handler.request.arguments = auth_args
        handler.request.get_argument = lambda x, strip=True: auth_args[x][0].decode()

        _ = await authenticator.authenticate(handler, None)
        assert mock_validator.called


async def test_authenticator_returns_auth_dict_when_custom_canvas_user_id_is_empty(
    auth_args,
):
    """
    Do we get a valid username when the custom_canvas_user_id is empty?
    """
    local_args = auth_args
    local_args["custom_canvas_user_id"] = [b""]
    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ):
        authenticator = MockLTI11Authenticator()
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(["key", "secret"])),
            request=Mock(
                arguments=local_args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            "name": "185d6c59731a553009ca9b59ca3a885100000",
        }
        assert result["name"] == expected["name"]


async def test_authenticator_returns_correct_username_when_using_lis_person_contact_email_primary(
    auth_args,
):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    local_authenticator = MockLTI11Authenticator()
    local_authenticator.username_key = "lis_person_contact_email_primary"
    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ):
        authenticator = local_authenticator
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(["key", "secret"])),
            request=Mock(
                arguments=auth_args,
                headers={},
                items=[],
            ),
        )
        result = await authenticator.authenticate(handler, None)
        expected = {
            "name": "student1@example.com",
        }
        assert result["name"] == expected["name"]


async def test_empty_username_raises_http_error(
    auth_args,
):
    """Does an empty username value raise the correct 400 HTTPError?"""
    local_authenticator = LTI11Authenticator()
    auth_args["custom_canvas_user_id"] = [b""]
    auth_args["user_id"] = [b""]

    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ):
        authenticator = local_authenticator
        handler = Mock(
            spec=RequestHandler,
            get_secure_cookie=Mock(return_value=json.dumps(["key", "secret"])),
            request=Mock(
                arguments=auth_args,
                headers={},
                items=[],
            ),
        )
        with pytest.raises(HTTPError):
            _ = await authenticator.authenticate(handler, None)
