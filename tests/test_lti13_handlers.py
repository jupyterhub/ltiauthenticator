import hashlib
from uuid import uuid4
from oauthenticator.oauth2 import _deserialize_state, _serialize_state

import pytest

from unittest.mock import patch

from ltiauthenticator.lti13.handlers import LTI13LoginHandler
from ltiauthenticator.lti13.authenticator import LTI13LaunchValidator
from ltiauthenticator.lti13.utils import convert_request_to_dict


@pytest.mark.asyncio
async def test_lti_13_login_handler_empty_authorize_url_env_var_raises_environment_error(
    monkeypatch, lti13_login_params, lti13_login_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler raise a missing argument error if request body doesn't have any
    arguments?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'foo.bar.tld')
    local_handler = make_mock_request_handler(LTI13LoginHandler)

    with patch.object(LTI13LaunchValidator, 'validate_launch_request', return_value=True):
        with patch.object(LTI13LoginHandler, 'redirect', return_value=None):
            with pytest.raises(EnvironmentError):
                LTI13LoginHandler(local_handler.application, local_handler.request).post()


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_convert_request_to_dict_method(
    monkeypatch, lti13_login_params, lti13_login_params_dict, make_mock_request_handler
):
    """
    Does the LTI13LoginHandler call the convert_request_to_dict function once it
    receiving the post request?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    with patch.object(LTI13LaunchValidator, 'validate_login_request', return_value=True):
        with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None):
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
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    with patch.object(
        LTI13LaunchValidator, 'validate_login_request', return_value=True
    ) as mock_validate_login_request:
        with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None):
            LTI13LoginHandler(local_handler.application, local_handler.request).post()
            assert mock_validate_login_request.called


@pytest.mark.asyncio
async def test_lti_13_login_handler_invokes_redirect_method(monkeypatch, lti13_auth_params, make_mock_request_handler):
    """
    Does the LTI13LoginHandler call the redirect function once it
    receiving the post request?
    """
    monkeypatch.setenv('LTI13_AUTHORIZE_URL', 'http://my.lms.platform/api/lti/authorize_redirect')
    local_handler = make_mock_request_handler(LTI13LoginHandler)
    with patch.object(LTI13LaunchValidator, 'validate_login_request', return_value=True):
        with patch.object(LTI13LoginHandler, 'authorize_redirect', return_value=None) as mock_redirect:
            LTI13LoginHandler(local_handler.application, local_handler.request).post()
            assert mock_redirect.called
