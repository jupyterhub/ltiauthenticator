"""
In this file we test LTI13Authenticator.authenticate with mocked responses from
LTI13LaunchValidator's methods, which are called by authenticate.

We have dedicated tests of LTI13LaunchValidator's methods in
test_lti13_validator.py.
"""

from tornado.web import RequestHandler

from ltiauthenticator.lti13.auth import LTI13Authenticator


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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
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

    result = await authenticator.authenticate(request_handler, launch_req_jwt_decoded)
    assert result["name"] == "usertest@example.com"
