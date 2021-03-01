from os import chmod
from os import environ

import pytest

from ltiauthenticator.lti13.handlers import LTI13JWKSHandler

from tornado.web import RequestHandler

from unittest.mock import patch


@pytest.mark.asyncio
async def test_get_method_raises_permission_error_if_pem_file_is_protected(
    lti13_config_environ, make_mock_request_handler
):
    """
    Is a permission error raised if the private key is protected after calling the
    handler's method?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)
    # change pem permission
    key_path = environ.get('LTI13_PRIVATE_KEY')
    chmod(key_path, 0o060)
    with pytest.raises(PermissionError):
        await config_handler.get()


@pytest.mark.asyncio
async def test_get_method_raises_an_error_without_lti13_private_key(make_mock_request_handler):
    """
    Is an environment error raised if the LTI13_PRIVATE_KEY env var is not set
    after calling the handler's method?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)
    with pytest.raises(EnvironmentError):
        await config_handler.get()


@patch('tornado.web.RequestHandler.write')
def test_get_method_calls_write_method_with_a_dict(mock_write_method, lti13_config_environ, make_mock_request_handler):
    """
    Does the write method is called with a dict?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)

    config_handler.get()
    assert mock_write_method.called
    write_args = mock_write_method.call_args[0]
    # make sure we're passing a dict to let tornado convert it as json with the specific content-type
    assert write_args[0]
    assert type(write_args[0]) == dict


def test_get_method_set_content_type_as_json(lti13_config_environ, make_mock_request_handler):
    """
    Does the write method is set the content-type header as application/json?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13JWKSHandler(handler.application, handler.request)

    config_handler.get()
    assert 'Content-Type' in config_handler._headers
    assert 'application/json' in config_handler._headers['Content-type']
