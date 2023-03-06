from unittest.mock import patch

import pytest
from tornado.httputil import HTTPServerRequest
from tornado.web import HTTPError

import ltiauthenticator.lti13.handlers
from ltiauthenticator.lti13.handlers import LTI13CallbackHandler, LTI13LoginInitHandler
from ltiauthenticator.lti13.validator import InvalidAudienceError, LTI13LaunchValidator
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
    args = {
        "login_hint": "something",
        "lti_message_hint": "some_lti_message_hint",
        "client_id": "itsme",
    }
    hub_uri = "https://hub.example.com"
    state = "my_state"
    nonce = "some_nonce"
    redirect_uri = "https://launch-from-here.com"
    handler = req_handler(
        LTI13LoginInitHandler,
        uri=f"{hub_uri}/?{'&'.join(f'{k}={v}' for k, v in args.items())}",
        method=method,
        authenticator=MockLTI13Authenticator(),
    )

    # mock nonce creation
    ltiauthenticator.lti13.handlers.get_nonce = lambda x: nonce

    with patch.object(
        LTI13LaunchValidator, "validate_login_request"
    ) as mock_validate_login_request, patch.object(
        handler, "authorize_redirect"
    ) as mock_authorize_redirect, patch.object(
        handler, "get_state", return_value=state
    ) as mock_get_state, patch.object(
        handler, "set_state_cookie"
    ) as mock_set_state_cookie, patch.object(
        handler, "get_redirect_uri", return_value=redirect_uri
    ) as mock_get_redicerect_uri:
        if method == "GET":
            handler.get()
        elif method == "POST":
            handler.post()
        mock_validate_login_request.assert_called_once()
        mock_get_state.assert_called_once()
        mock_set_state_cookie.assert_called_once()
        mock_get_redicerect_uri.assert_called_once()
        mock_authorize_redirect.assert_called_once_with(
            **args,
            nonce=nonce,
            state=state,
            redirect_uri=redirect_uri,
        )


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


async def test_lti13_callback_handler_post_invocation(req_handler):
    """Test invokation of parameter, token and state validation."""
    authenticator = MockLTI13Authenticator()
    decoded_jwt = "decoded_abc"
    username = "somebody"
    handler = req_handler(
        LTI13CallbackHandler,
        uri="https://hub.example.com/",
        authenticator=authenticator,
    )

    with patch.object(
        handler, "decode_and_validate_launch_request", return_value=decoded_jwt
    ) as mock_validate, patch.object(
        handler, "login_user", return_value=username
    ) as mock_login_user, patch.object(
        handler, "redirect_to_next_url"
    ) as mock_redirect_to_next_url:
        await handler.post()
        mock_validate.assert_called_once()
        mock_login_user.assert_called_once_with(decoded_jwt)
        mock_redirect_to_next_url.assert_called_once_with(username)


async def test_lti13_callback_handler_post_raises_403_on_non_user(req_handler):
    """Test invokation of parameter, token and state validation."""
    authenticator = MockLTI13Authenticator()
    handler = req_handler(
        LTI13CallbackHandler,
        uri="https://hub.example.com/",
        authenticator=authenticator,
    )
    with patch.object(handler, "decode_and_validate_launch_request"), patch.object(
        handler, "login_user", return_value=None
    ):
        with pytest.raises(HTTPError) as e_info:
            await handler.post()
        assert str(e_info.value) == "HTTP 403: Forbidden (User missing or null)"


async def test_lti13_callback_handler_post_raises_401_on_invalid_audience(req_handler):
    """Test invokation of parameter, token and state validation."""
    authenticator = MockLTI13Authenticator()
    handler = req_handler(
        LTI13CallbackHandler,
        uri="https://hub.example.com/",
        authenticator=authenticator,
    )

    def raiser():
        raise InvalidAudienceError("Invalid Audience")

    with patch.object(handler, "decode_and_validate_launch_request", raiser):
        with pytest.raises(HTTPError) as e_info:
            await handler.post()
        assert str(e_info.value) == "HTTP 401: Unauthorized (Invalid Audience)"


async def test_lti13_callback_handler_decode_and_validate_launch_request_invocation(
    req_handler,
):
    """Test invokation of parameter, token and state validation."""
    authenticator = MockLTI13Authenticator()
    id_token = "abc"
    decoded_jwt = "decoded_abc"
    handler = req_handler(
        LTI13CallbackHandler,
        uri=f"https://hub.example.com/?id_token={id_token}",
        authenticator=authenticator,
    )

    with patch.object(
        LTI13LaunchValidator, "validate_auth_response"
    ) as mock_validate_auth_response, patch.object(
        handler, "check_state"
    ) as mock_check_state, patch.object(
        LTI13LaunchValidator, "verify_and_decode_jwt", return_value=decoded_jwt
    ) as mock_verify_and_decode_jwt, patch.object(
        LTI13LaunchValidator, "validate_id_token"
    ) as mock_validate_id_token, patch.object(
        LTI13LaunchValidator, "validate_azp_claim"
    ) as mock_validate_azp_claim:
        handler.decode_and_validate_launch_request()

        mock_validate_auth_response.assert_called_once()
        mock_check_state.assert_called_once()
        mock_verify_and_decode_jwt.assert_called_once_with(
            encoded_jwt=id_token,
            issuer=authenticator.issuer,
            audience=authenticator.client_id,
            jwks_endpoint=authenticator.endpoint,
            jwks_algorithms=authenticator.jwks_algorithms,
        )
        mock_validate_id_token.assert_called_once_with(decoded_jwt)
        mock_validate_azp_claim.assert_called_once_with(
            decoded_jwt, authenticator.client_id
        )
