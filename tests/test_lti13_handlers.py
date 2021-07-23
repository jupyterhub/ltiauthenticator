import hashlib
from unittest.mock import patch
from uuid import uuid4

import pytest
from unittest import mock
from oauthenticator.oauth2 import _deserialize_state
from oauthenticator.oauth2 import _serialize_state

from ltiauthenticator.lti13.auth import LTI13LaunchValidator
from ltiauthenticator.lti13.handlers import LTI13LoginHandler
from ltiauthenticator.utils import convert_request_to_dict


@pytest.mark.asyncio
async def test_lti_13_login_handler_empty_authorize_url_env_var_raises_environment_error(
    monkeypatch, lti13_login_params, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler raise a missing argument error if request body doesn't have any
    arguments?
    """
    monkeypatch.setenv("OAUTH2_AUTHORIZE_URL", "")
    local_handler = make_mock_request_handler(LTI13LoginHandler)

    with patch.object(
        LTI13LaunchValidator, "validate_launch_request", return_value=True
    ):
        with patch.object(LTI13LoginHandler, "redirect", return_value=None):
            with pytest.raises(EnvironmentError):
                LTI13LoginHandler(
                    local_handler.application, local_handler.request
                ).post()


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_convert_request_to_dict_method(
    monkeypatch, lti13_login_params, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the LTIUtils convert_request_to_dict function once it
    receiving the post request?
    """
    monkeypatch.setenv(
        "OAUTH2_AUTHORIZE_URL", "http://my.lms.platform/api/lti/authorize_redirect"
    )
    local_handler = make_mock_request_handler(LTI13LoginHandler)

    with patch.object(
        LTI13LaunchValidator, "validate_login_request", return_value=True
    ):
        with patch.object(LTI13LoginHandler, "authorize_redirect", return_value=None):
            LTI13LoginHandler(local_handler.application, local_handler.request).post()
            assert convert_request_to_dict.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_validate_login_request_method(
    monkeypatch, lti13_auth_params, lti13_auth_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the LTI13LaunchValidator validate_login_request function once it
    receiving the post request?
    """
    monkeypatch.setenv(
        "LTI13_AUTHORIZE_URL", "http://my.lms.platform/api/lti/authorize_redirect"
    )
    local_handler = make_mock_request_handler(LTI13LoginHandler)

    with mock.patch("convert_request_to_dict", return_value=lti13_auth_params_dict):
        with patch.object(
            LTI13LaunchValidator, "validate_login_request", return_value=True
        ) as mock_validate_login_request:
            with patch.object(
                LTI13LoginHandler, "authorize_redirect", return_value=None
            ):
                LTI13LoginHandler(
                    local_handler.application, local_handler.request
                ).post()
                assert mock_validate_login_request.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_redirect_method(
    monkeypatch, lti13_auth_params, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the redirect function once it
    receiving the post request?
    """
    monkeypatch.setenv(
        "LTI13_AUTHORIZE_URL", "http://my.lms.platform/api/lti/authorize_redirect"
    )
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    with mock.patch(
        "convert_request_to_dict",
        return_value=convert_request_to_dict(lti13_auth_params),
    ):
        with patch.object(
            LTI13LaunchValidator, "validate_login_request", return_value=True
        ):
            with patch.object(
                LTI13LoginHandler, "authorize_redirect", return_value=None
            ) as mock_redirect:
                LTI13LoginHandler(
                    local_handler.application, local_handler.request
                ).post()
                assert mock_redirect.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_calls_authorize_redirect_with_correct_values(
    monkeypatch, lti13_auth_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler correctly set all variables needed for the redict method
    after receiving it from the validator?
    """
    expected = lti13_auth_params_dict
    monkeypatch.setenv(
        "LTI13_AUTHORIZE_URL", "http://my.lms.platform/api/lti/authorize_redirect"
    )
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    state_id = uuid4().hex
    expected_state = _serialize_state({"state_id": state_id, "next_url": ""})
    with mock.patch("convert_request_to_dict", return_value=lti13_auth_params_dict):
        with patch.object(
            LTI13LaunchValidator, "validate_login_request", return_value=True
        ):
            with patch.object(
                LTI13LoginHandler, "get_state", return_value=expected_state
            ):
                with patch.object(
                    LTI13LoginHandler, "authorize_redirect", return_value=None
                ) as mock_auth_redirect:
                    nonce_raw = hashlib.sha256(expected_state.encode())
                    expected_nonce = nonce_raw.hexdigest()

                    LTI13LoginHandler(
                        local_handler.application, local_handler.request
                    ).post()
                    assert mock_auth_redirect.called

                    mock_auth_redirect.assert_called_with(
                        client_id=expected["client_id"],
                        login_hint=expected["login_hint"],
                        lti_message_hint=expected["lti_message_hint"],
                        redirect_uri="https://127.0.0.1/hub/oauth_callback",
                        state=expected_state,
                        nonce=expected_nonce,
                    )


@pytest.mark.asyncio
async def test_lti_13_login_handler_sets_state_with_next_url_obtained_from_target_link_uri(
    monkeypatch,
    mocker,
    lti13_login_params_decoded,
    lti13_login_params,
    make_mock_request_handler,
):
    """
    Do we get the expected nonce value result after hashing the state and returning the
    hexdigest?
    """
    monkeypatch.setenv(
        "OAUTH2_AUTHORIZE_URL", "http://my.lms.platform/api/lti/authorize_redirect"
    )
    lti13_login_params["target_link_uri"] = [
        (
            lti13_login_params["target_link_uri"][0].decode()
            + "?next=/user-redirect/lab"
        ).encode()
    ]
    local_handler = make_mock_request_handler(LTI13LoginHandler)

    # with mocker.patch("convert_request_to_dict", return_value=lti13_login_params_decoded):
    with patch.object(
        LTI13LaunchValidator, "validate_login_request", return_value=True
    ):
        with patch.object(LTI13LoginHandler, "authorize_redirect", return_value=None):
            expected_state_json = {
                "state_id": "6f0ec1569a3a402dac61626361d0c125",
                "next_url": "/user-redirect/lab",
            }

            login_instance = LTI13LoginHandler(
                local_handler.application, local_handler.request
            )
            login_instance.post()
            assert login_instance._state
            state_decoded = _deserialize_state(login_instance._state)
            state_decoded["next_url"] == expected_state_json["next_url"]
