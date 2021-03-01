import pem
import pytest
import os

from unittest.mock import patch

from ltiauthenticator.lti13.utils import get_lms_access_token
from ltiauthenticator.lti13.utils import get_pem_text_from_file


def test_get_pem_text_from_file_raises_an_error_if_pem_cannot_be_read():
    with pytest.raises(PermissionError):
        get_pem_text_from_file('file.pem')


def test_get_pem_text_from_file_raises_an_error_if_parse_method_returns_empty_list():
    with patch.object(pem, 'parse_file', return_value=[]) as mock_pem_parse_file:
        with pytest.raises(Exception):
            get_pem_text_from_file('file.pem')


def test_get_pem_text_from_file_parses_the_pem_file(lti13_config_environ):
    pem_key = os.environ.get('LTI13_PRIVATE_KEY')
    certs = pem.parse_file(pem_key)
    with patch.object(pem, 'parse_file', return_value=certs) as mock_pem_parse_file:
        get_pem_text_from_file(pem_key)
        assert mock_pem_parse_file.called


@pytest.mark.asyncio
@patch('ltiauthenticator.lti13.utils.get_pem_text_from_file')
@patch('ltiauthenticator.lti13.utils.get_headers_to_jwt_encode')
async def test_get_lms_access_token_calls_get_pem_text_from_file(
    mock_get_headers_to_jwt, mock_get_pem_text, lti13_config_environ, http_async_httpclient_with_simple_response
):
    pem_key = os.environ.get('LTI13_PRIVATE_KEY')
    mock_get_headers_to_jwt.return_value = None
    mock_get_pem_text.return_value = pem.parse_file(pem_key)[0].as_text()
    # here we're using a httpclient mocked
    await get_lms_access_token('url', pem_key, 'client-id')
    assert mock_get_pem_text.called
