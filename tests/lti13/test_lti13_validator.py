import pytest

from ltiauthenticator.lti13.validator import (
    IncorrectValueError,
    LTI13LaunchValidator,
    MissingRequiredArgumentError,
    TokenError,
)


# Tests of validate_login_request()
# -------------------------------------------------------------------------------
def test_validate_login_request_with_invalid_data():
    validator = LTI13LaunchValidator()

    with pytest.raises(MissingRequiredArgumentError):
        validator.validate_login_request({"key1": "value1"})


# Tests of verify_and_decode_jwt()
# -------------------------------------------------------------------------------
def test_validate_verify_and_decode_jwt(launch_req_jwt, launch_req_jwt_decoded):
    # FIXME: We make a request to an external website that could go down. If it
    #        does, there is a currently unused fixture called
    #        jwks_endpoint_response that could be used.
    #
    validator = LTI13LaunchValidator()
    result = validator.verify_and_decode_jwt(
        encoded_jwt=launch_req_jwt,
        issuer=launch_req_jwt_decoded["iss"],
        audience="client1",
        jwks_endpoint="https://lti-ri.imsglobal.org/platforms/3691/platform_keys/3396.json",
        jwks_algorithms=["RS256"],
        # mocked launch_req_jwt has expired and we ignore that here
        options={"verify_exp": False},
    )
    assert result == launch_req_jwt_decoded


def test_verify_and_decode_jwt_fails_on_incorrect_iss(
    launch_req_jwt, launch_req_jwt_decoded
):
    # FIXME: We make a request to an external website that could go down. If it
    #        does, there is a currently unused fixture called
    #        jwks_endpoint_response that could be used.
    #
    validator = LTI13LaunchValidator()
    with pytest.raises(TokenError) as e:
        validator.verify_and_decode_jwt(
            encoded_jwt=launch_req_jwt,
            issuer=launch_req_jwt_decoded["iss"] + "/something_wrong",
            audience="client1",
            jwks_endpoint="https://lti-ri.imsglobal.org/platforms/3691/platform_keys/3396.json",
            jwks_algorithms=["RS256"],
            # mocked launch_req_jwt has expired and we ignore that here
            options={"verify_exp": False},
        )
        assert str(e) == "Invalid issuer"


def test_verify_and_decode_jwt_fails_on_incorrect_aud(
    launch_req_jwt, launch_req_jwt_decoded
):
    # FIXME: We make a request to an external website that could go down. If it
    #        does, there is a currently unused fixture called
    #        jwks_endpoint_response that could be used.
    #
    validator = LTI13LaunchValidator()
    with pytest.raises(TokenError) as e:
        validator.verify_and_decode_jwt(
            encoded_jwt=launch_req_jwt,
            issuer=launch_req_jwt_decoded["iss"],
            audience="client1" + "_something_wrong",
            jwks_endpoint="https://lti-ri.imsglobal.org/platforms/3691/platform_keys/3396.json",
            jwks_algorithms=["RS256"],
            # mocked launch_req_jwt has expired and we ignore that here
            options={"verify_exp": False},
        )
        assert str(e) == "Invalid audience"


# Tests of validate_launch_request()
# -------------------------------------------------------------------------------
def test_validate_minimal_launch_request(minimal_launch_req_jwt_decoded):
    """
    Is the JWT valid if it contains only the claims required by the LTI 1.3 specs?

    Ref: https://www.imsglobal.org/spec/lti/v1p3#required-message-claims
    """
    validator = LTI13LaunchValidator()
    validator.validate_id_token(minimal_launch_req_jwt_decoded)


# Tests of validate_launch_request()
# -------------------------------------------------------------------------------
def test_validate_launch_request_empty_roles(launch_req_jwt_decoded):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/roles"] = ""

    validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_invalid_message_type(launch_req_jwt_decoded):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded[
        "https://purl.imsglobal.org/spec/lti/claim/message_type"
    ] = "???"

    with pytest.raises(IncorrectValueError):
        validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_invalid_version(launch_req_jwt_decoded):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded[
        "https://purl.imsglobal.org/spec/lti/claim/version"
    ] = "1.0.0"

    with pytest.raises(IncorrectValueError):
        validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_empty_deployment_id(
    launch_req_jwt_decoded,
):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded[
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
    ] = ""

    validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_empty_target_link_uri(
    launch_req_jwt_decoded,
):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded[
        "https://purl.imsglobal.org/spec/lti/claim/target_link_uri"
    ] = ""

    validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_empty_resource_link_id(
    launch_req_jwt_decoded,
):
    validator = LTI13LaunchValidator()
    launch_req_jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/resource_link"][
        "id"
    ] = ""

    with pytest.raises(MissingRequiredArgumentError):
        validator.validate_id_token(launch_req_jwt_decoded)


def test_validate_launch_request_with_priv(
    launch_req_jwt_decoded_priv,
):
    validator = LTI13LaunchValidator()

    validator.validate_id_token(launch_req_jwt_decoded_priv)
