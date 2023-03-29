"""
In this file we test LTI13Authenticator.authenticate with mocked responses from
LTI13LaunchValidator's methods, which are called by authenticate.

We have dedicated tests of LTI13LaunchValidator's methods in
test_lti13_validator.py.
"""
import pytest
from tornado.web import RequestHandler

from ltiauthenticator.lti13.auth import LTI13Authenticator, LoginError
from ltiauthenticator.lti13.constants import LTI13_CUSTOM_CLAIM


async def test_authenticator_returned_username_with_sub(
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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert result["name"] == launch_req_jwt_decoded["sub"]


async def test_authenticator_returned_username_with_sub_and_email(
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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert result["name"] == launch_req_jwt_decoded["email"]


async def test_authenticator_returned_username_with_sub_email_name(
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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert result["name"] == launch_req_jwt_decoded["email"]


async def test_authenticator_returned_username_from_custom_claim(
    req_handler,
    launch_req_jwt_decoded,
):
    """
    Is name set correctly in the authenticate method's response, based on being
    provided a custom claim?
    """
    authenticator = LTI13Authenticator()
    authenticator.username_key = "custom_uname"
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    launch_req_jwt_decoded[LTI13_CUSTOM_CLAIM] = {"uname": "jovyan.jupyter"}

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert result["name"] == launch_req_jwt_decoded[LTI13_CUSTOM_CLAIM]["uname"]


async def test_authenticator_raises_login_error_if_username_key_not_found(
    req_handler,
    launch_req_jwt_decoded,
):
    """
    Is name set correctly in the authenticate method's response, based on being
    provided sub, name, and email?
    """
    authenticator = LTI13Authenticator()
    authenticator.username_key = "does_not_exist"
    launch_req_jwt_decoded.pop("sub", None)
    request_handler = req_handler(RequestHandler, authenticator=authenticator)

    with pytest.raises(LoginError) as e:
        _ = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert str(e.value) == "Unable to set the username with username_key does_not_exist"
