from unittest.mock import patch

import pytest
from tornado.web import RequestHandler

from ltiauthenticator.lti13.auth import LTI13Authenticator
from ltiauthenticator.lti13.auth import LTI13LaunchValidator


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_handler_get_argument(
    build_lti13_jwt_id_token,
    make_lti13_resource_link_request,
    make_mock_request_handler,
):
    """
    Does the authenticator invoke the RequestHandler get_argument method?
    """
    authenticator = LTI13Authenticator()

    request_handler = make_mock_request_handler(
        RequestHandler, authenticator=authenticator
    )
    with patch.object(
        request_handler,
        "get_argument",
        return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request),
    ) as mock_get_argument:
        _ = await authenticator.authenticate(request_handler, None)
        assert mock_get_argument.called


@pytest.mark.asyncio
async def test_authenticator_invokes_lti13validator_validate_launch_request(
    make_lti13_resource_link_request,
    build_lti13_jwt_id_token,
    make_mock_request_handler,
):
    """
    Does the authenticator invoke the LTI13Validator validate_launch_request method?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(
        RequestHandler, authenticator=authenticator
    )
    with patch.object(
        RequestHandler,
        "get_argument",
        return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request),
    ):
        with patch.object(
            LTI13LaunchValidator, "validate_launch_request", return_value=True
        ) as mock_verify_authentication_request:
            _ = await authenticator.authenticate(request_handler, None)
            assert mock_verify_authentication_request.called


@pytest.mark.asyncio
async def test_authenticator_returns_auth_state_name_from_lti13_email_claim(
    make_lti13_resource_link_request,
    build_lti13_jwt_id_token,
    make_mock_request_handler,
):
    """
    Do we get a valid username when only including an email to the resource link request?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(
        RequestHandler, authenticator=authenticator
    )
    lti13_json = make_lti13_resource_link_request
    lti13_json["name"] = ""
    lti13_json["given_name"] = ""
    lti13_json["family_name"] = ""
    lti13_json["email"] = "usertest@example.com"
    with patch.object(
        RequestHandler,
        "get_argument",
        return_value=build_lti13_jwt_id_token(lti13_json),
    ):
        with patch.object(
            LTI13LaunchValidator, "validate_launch_request", return_value=True
        ):
            result = await authenticator.authenticate(request_handler, None)
            assert result["name"] == "usertest@example.com"


@pytest.mark.asyncio
async def test_authenticator_returns_username_in_auth_state_with_privacy_enabled(
    make_lti13_resource_link_request,
    build_lti13_jwt_id_token,
    make_mock_request_handler,
):
    """
    Do we get a valid username when privacy is enabled?
    """
    authenticator = LTI13Authenticator()
    request_handler = make_mock_request_handler(
        RequestHandler, authenticator=authenticator
    )
    make_lti13_resource_link_request["name"] = ""
    make_lti13_resource_link_request["given_name"] = ""
    make_lti13_resource_link_request["family_name"] = ""
    make_lti13_resource_link_request["email"] = ""
    make_lti13_resource_link_request["https://purl.imsglobal.org/spec/lti/claim/lis"][
        "person_sourcedid"
    ] = ""

    with patch.object(
        RequestHandler,
        "get_argument",
        return_value=build_lti13_jwt_id_token(make_lti13_resource_link_request),
    ):
        with patch.object(
            LTI13LaunchValidator, "validate_launch_request", return_value=True
        ):
            result = await authenticator.authenticate(request_handler, None)

            assert result["name"] == "8171934b-f5e2-4f4e-bdbd-6d798615b93e"
