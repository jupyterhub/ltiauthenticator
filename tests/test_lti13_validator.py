import pytest
from tornado.web import HTTPError

from ltiauthenticator.lti13.validator import LTI13LaunchValidator


def test_validate_empty_roles_claim_value(make_lti13_resource_link_request):
    """
    Is the JWT valid with an empty roles claim value?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/roles"] = ""

    assert validator.validate_launch_request(jws)


def test_validate_missing_required_claims_in_step_1_resource_link_request():
    """
    Is the JWT valid with an incorrect message type claim?
    """
    validator = LTI13LaunchValidator()
    fake_jws = {
        "key1": "value1",
    }

    with pytest.raises(HTTPError):
        validator.validate_login_request(fake_jws)


def test_validate_missing_required_claims_in_step_2_resource_link_request():
    """
    Is the JWT valid with an incorrect message type claim?
    """
    validator = LTI13LaunchValidator()
    fake_jws = {
        "key1": "value1",
    }

    with pytest.raises(HTTPError):
        validator.validate_login_request(fake_jws)


def test_validate_invalid_resource_link_request_message_type_claim_value(
    make_lti13_resource_link_request,
):
    """
    Is the JWT valid with an incorrect message type claim?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/message_type"] = "FakeLinkRequest"

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_invalid_version_request_claim_value(make_lti13_resource_link_request):
    """
    Is the JWT valid with an incorrect version claim?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/version"] = "1.0.0"

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_empty_deployment_id_request_claim_value(
    make_lti13_resource_link_request,
):
    """
    Is the JWT valid with an empty deployment_id claim?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/deployment_id"] = ""

    assert validator.validate_launch_request(jws) is True


def test_validate_empty_target_link_uri_request_claim_value(
    make_lti13_resource_link_request,
):
    """
    Is the JWT valid with an empty target link uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"] = ""

    assert validator.validate_launch_request(jws) is True


def test_validate_empty_resource_link_id_request_claim_value(
    make_lti13_resource_link_request,
):
    """
    Is the JWT valid with an empty resource request id uri claim?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request
    jws["https://purl.imsglobal.org/spec/lti/claim/resource_link"]["id"] = ""

    with pytest.raises(HTTPError):
        validator.validate_launch_request(jws)


def test_validate_claim_values_with_privacy_enabled(
    make_lti13_resource_link_request_privacy_enabled,
):
    """
    Is the JWT valid when privacy is enabled?
    """
    validator = LTI13LaunchValidator()
    jws = make_lti13_resource_link_request_privacy_enabled

    assert validator.validate_launch_request(jws)
