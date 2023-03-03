from unittest.mock import patch

import pytest
from tornado.httputil import HTTPServerRequest

from ltiauthenticator.lti13.handlers import LTI13CallbackHandler, LTI13LoginInitHandler
from ltiauthenticator.lti13.validator import LTI13LaunchValidator
from ltiauthenticator.utils import convert_request_to_dict

from .mocking import MockLTI13Authenticator


async def test_lti_13_handler_paths(app):
    """Test if all handlers are correctly set with the LTI13Authenticator."""
    auth = MockLTI13Authenticator()
    handlers = auth.get_handlers(app)
    handler_paths = [route[0] for route in handlers]
    assert "lti13/config" in handler_paths
    assert "lti13/oauth_login" in handler_paths
    assert "lti13/oauth_callback" in handler_paths


@pytest.mark.parametrize("method", ["GET", "POST"])
async def test_lti13_login_init_handler_invocation(method, req_handler):
    """Test invokation of parameter validation, setting of state cookie and authorization redirection."""
    handler = req_handler(
        LTI13LoginInitHandler,
        uri="https://hub.example.com/?login_hint=something",
        method=method,
        authenticator=MockLTI13Authenticator(),
    )

    with patch.object(
        LTI13LaunchValidator, "validate_login_request"
    ) as mock_validate_login_request, patch.object(
        handler, "authorize_redirect"
    ) as mock_authorize_redirect, patch.object(
        handler, "set_state_cookie"
    ) as mock_set_state_cookie:
        if method == "GET":
            handler.get()
        elif method == "POST":
            handler.post()
        mock_validate_login_request.assert_called_once()
        mock_authorize_redirect.assert_called_once()
        mock_set_state_cookie.assert_called_once()


async def test_lti13_login_init_handler_auth_request_contains_required_arguments(
    req_handler,
):
    authenticator = MockLTI13Authenticator()
    handler = req_handler(
        LTI13LoginInitHandler,
        authenticator=authenticator,
    )

    fixed_paramter = {
        "response_type": "id_token",
        "scope": "openid",
        "response_mode": "form_post",
        "prompt": "none",
    }
    dynamic_parameter = {
        "client_id": "some_client_id",
        "redirect_uri": "some_redirect_uri",
        "login_hint": "some_login_hint",
        "nonce": "some_nonce",
        "state": "some_state",
    }
    expected = {**fixed_paramter, **dynamic_parameter}

    with patch.object(handler, "redirect") as mock_redirect:
        handler.authorize_redirect(**dynamic_parameter)
        mock_redirect.assert_called_once()
        redirect_uri = mock_redirect.call_args[0][0]
        request = HTTPServerRequest(uri=redirect_uri)
        args = convert_request_to_dict(request.arguments)

        for k in expected:
            assert k in args
            assert expected[k] == args[k]


async def test_lti13_callback_handler_invocation(req_handler):
    """Test invokation of parameter, token and state validation."""
    id_token = "abc"
    decoded_jwt = "decoded_abc"
    aud = "its_me"
    endpoint = "https://some-url.com/jwk"
    jwks_algorithms = ["RS256"]
    username = "somebody"
    handler = req_handler(
        LTI13CallbackHandler,
        uri=f"https://hub.example.com/?id_token={id_token}",
        authenticator=MockLTI13Authenticator(),
    )

    handler.client_id = aud
    handler.endpoint = endpoint
    handler.jwks_algorithms = jwks_algorithms

    with patch.object(
        LTI13LaunchValidator, "validate_auth_response"
    ) as mock_validate_auth_response, patch.object(
        LTI13LaunchValidator, "verify_and_decode_jwt", return_value=decoded_jwt
    ) as mock_verify_and_decode_jwt, patch.object(
        LTI13LaunchValidator, "validate_id_token"
    ) as mock_validate_id_token, patch.object(
        handler, "check_state"
    ) as mock_check_state, patch.object(
        handler, "login_user", return_value=username
    ) as mock_login_user, patch.object(
        handler, "redirect_to_next_url"
    ) as mock_redirect_to_next_url:
        await handler.post()
        mock_validate_auth_response.assert_called_once()
        mock_verify_and_decode_jwt.assert_called_once_with(
            id_token,
            audience=aud,
            jwks_endpoint=endpoint,
            jwks_algorithms=jwks_algorithms,
        )
        mock_validate_id_token.assert_called_once_with(decoded_jwt)
        mock_check_state.assert_called_once()
        mock_login_user.assert_called_once_with(decoded_jwt)
        mock_redirect_to_next_url.assert_called_once_with(username)
