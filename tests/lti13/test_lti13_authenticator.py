"""
In this file we test LTI13Authenticator.authenticate with mocked responses from
LTI13LaunchValidator's methods, which are called by authenticate.

We have dedicated tests of LTI13LaunchValidator's methods in
test_lti13_validator.py.
"""

from unittest.mock import patch

from tornado.web import RequestHandler

from ltiauthenticator.lti13.auth import LTI13Authenticator, LTI13LaunchValidator


async def test_authenticator_invokations(req_handler):
    """
    Does the authenticator invoke the following methods?
    - the provided RequestHandler's get_argument
    - the LTI13LaunchValidator's verify_and_decode_jwt
    - the LTI13LaunchValidator's validate_id_token
    """
    authenticator = LTI13Authenticator()
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    with patch.object(
        request_handler, "get_argument"
    ) as mock_get_argument, patch.object(
        LTI13LaunchValidator, "verify_and_decode_jwt"
    ) as mock_verify_and_decode_jwt, patch.object(
        LTI13LaunchValidator, "validate_id_token"
    ) as mock_validate_id_token:
        await authenticator.authenticate(request_handler, None)
        assert mock_get_argument.called
        assert mock_verify_and_decode_jwt.called
        assert mock_validate_id_token.called


async def test_authenticator_returned_name_with_sub(
    req_handler,
    launch_req_jwt_decoded,
):
    """
    Is name set correctly in the authenticate method's response, based on being
    provided just the "sub" claim as information? This is relevant when privacy
    mode is enabled, and fields like email isn't provided.
    """
    authenticator = LTI13Authenticator()
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    launch_req_jwt_decoded.pop("name", None)
    launch_req_jwt_decoded.pop("given_name", None)
    launch_req_jwt_decoded.pop("family_name", None)
    launch_req_jwt_decoded.pop("email", None)
    launch_req_jwt_decoded.pop("https://purl.imsglobal.org/spec/lti/claim/lis", None)

    with patch.object(request_handler, "get_argument"), patch.object(
        LTI13LaunchValidator,
        "verify_and_decode_jwt",
        return_value=launch_req_jwt_decoded,
    ), patch.object(LTI13LaunchValidator, "validate_id_token"):
        result = await authenticator.authenticate(request_handler, None)
        assert result["name"] == "1ace7501877e6a429fca"


async def test_authenticator_returned_name_with_sub_and_email(
    req_handler,
    launch_req_jwt_decoded,
):
    """
    Is name set correctly in the authenticate method's response, based on being
    provided both sub and email?
    """
    authenticator = LTI13Authenticator()
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    launch_req_jwt_decoded.pop("name", None)
    launch_req_jwt_decoded.pop("given_name", None)
    launch_req_jwt_decoded.pop("family_name", None)
    launch_req_jwt_decoded["email"] = "usertest@example.com"

    with patch.object(request_handler, "get_argument"), patch.object(
        LTI13LaunchValidator,
        "verify_and_decode_jwt",
        return_value=launch_req_jwt_decoded,
    ), patch.object(LTI13LaunchValidator, "validate_id_token"):
        result = await authenticator.authenticate(request_handler, None)
        assert result["name"] == "usertest@example.com"


async def test_authenticator_returned_name_with_sub_email_name(
    req_handler,
    launch_req_jwt_decoded,
):
    """
    Is name set correctly in the authenticate method's response, based on being
    provided sub, name, and email?
    """
    authenticator = LTI13Authenticator()
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    launch_req_jwt_decoded["name"] = "Jovyan Jupyter"
    launch_req_jwt_decoded["given_name"] = "Jovyan"
    launch_req_jwt_decoded["family_name"] = "Jupyter"
    launch_req_jwt_decoded["email"] = "usertest@example.com"

    with patch.object(request_handler, "get_argument"), patch.object(
        LTI13LaunchValidator,
        "verify_and_decode_jwt",
        return_value=launch_req_jwt_decoded,
    ), patch.object(LTI13LaunchValidator, "validate_id_token"):
        result = await authenticator.authenticate(request_handler, None)
        assert result["name"] == "usertest@example.com"
