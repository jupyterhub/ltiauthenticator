import json

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from tornado.web import HTTPError
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler

from ltiauthenticator.lti11.auth import LTI11Authenticator
from ltiauthenticator.lti11.validator import LTI11LaunchValidator


@pytest.mark.asyncio
async def test_authenticator_uses_lti11validator(
    make_lti11_success_authentication_request_args,
):
    """
    Ensure that we call the LTI11Validator from the LTI11Authenticator.
    """
    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ) as mock_validator:

        authenticator = LTI11Authenticator()
        handler = Mock(spec=RequestHandler)
        request = HTTPServerRequest(
            method="POST",
            connection=Mock(),
        )
        handler.request = request

        handler.request.arguments = make_lti11_success_authentication_request_args(
            "lmsvendor"
        )
        handler.request.get_argument = (
            lambda x, strip=True: make_lti11_success_authentication_request_args(
                "lmsvendor"
            )[x][0].decode()
        )

        _ = await authenticator.authenticate(handler, None)
        assert mock_validator.called


@pytest.mark.asyncio
async def test_authenticator_returns_auth_state_with_other_lms_vendor(
    make_lti11_success_authentication_request_args,
):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    local_args = make_lti11_success_authentication_request_args()
    local_args["custom_canvas_user_id"] = ["".encode()]
    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ):
        authenticator = LTI11Authenticator()
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


@pytest.mark.asyncio
async def test_authenticator_returns_correct_username_when_using_lis_person_contact_email_primary(
    make_lti11_success_authentication_request_args,
):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    local_args = make_lti11_success_authentication_request_args()
    local_authenticator = LTI11Authenticator()
    local_authenticator.username_key = "lis_person_contact_email_primary"

    with patch.object(
        LTI11LaunchValidator, "validate_launch_request", return_value=True
    ):
        authenticator = local_authenticator
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
            "name": "student1@example.com",
        }
        assert result["name"] == expected["name"]


def test_launch(make_lti11_basic_launch_request_args):
    """Test a basic launch request"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)


def test_wrong_oauth_consumer_key(make_lti11_basic_launch_request_args):
    """Test that the request is rejected when receiving the wrong consumer key."""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({"wrongkey": oauth_consumer_secret})

    with pytest.raises(HTTPError):
        assert validator.validate_launch_request(launch_url, headers, args)


def test_wrong_oauth_consumer_secret(make_lti11_basic_launch_request_args):
    """Test that a request is rejected when the signature is created with the wrong secret."""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: "wrongsecret"})

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


@pytest.mark.asyncio
async def test_authenticator_returns_auth_state_with_other_lms_vendor_test(
    make_lti11_basic_launch_request_args, make_mock_request_handler
):
    """
    Do we get a valid username with lms vendors other than canvas?
    """
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)


def test_full_replay(make_lti11_basic_launch_request_args):
    """Ensure that an oauth timestamp/nonce replay raises an HTTPError"""

    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_partial_replay_timestamp(make_lti11_basic_launch_request_args):
    """Test that a partial timestamp replay raises an HTTPError."""

    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["oauth_timestamp"] = str(int(float(args["oauth_timestamp"])) - 1)
    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_partial_replay_nonce(make_lti11_basic_launch_request_args):
    """Test that a partial nonce replay raises an HTTPError"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["oauth_nonce"] = args["oauth_nonce"] + "1"
    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_dubious_extra_args(make_lti11_basic_launch_request_args):
    """Ensure that dubious extra args are rejected"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["extra_credential"] = "i have admin powers"
    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)
