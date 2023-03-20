from typing import Dict, Tuple

import pytest
from tornado.web import HTTPError

from ltiauthenticator.lti11.validator import LTI11LaunchValidator


def args_test_setup(
    arg_func, key: str = "my_consumer_key", secret: str = "my_shared_secret", **kwargs
) -> Tuple[LTI11LaunchValidator, str, Dict[str, str], Dict[str, str]]:
    """Common test setup logic"""
    launch_url, headers, args = arg_func(
        oauth_consumer_key=key, oauth_consumer_secret=secret, **kwargs
    )
    validator = LTI11LaunchValidator({key: secret})
    return validator, launch_url, headers, args


def test_basic_lti11_launch_request(get_launch_args):
    """
    Does a standard launch request work?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    assert validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_nonce_key(get_launch_args):
    """
    Does the launch request work with a missing oauth_nonce key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_nonce"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_nonce_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_nonce value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_nonce"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_timestamp_key(get_launch_args):
    """
    Does the launch request work with a missing oauth_timestamp key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_timestamp"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_consumer_key_key(
    get_launch_args,
):
    """
    Does the launch request work with a missing oauth_consumer_key key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_consumer_key"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_consumer_key_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_consumer_key value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_consumer_key"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_fake_oauth_consumer_key_value(
    get_launch_args,
):
    """
    Does the launch request work when the consumer_key isn't correct?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_consumer_key"] = [b"fake_consumer_key"][0].decode("utf-8")
        assert validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_signature_method_key(
    get_launch_args,
):
    """
    Does the launch request work with a missing oauth_signature_method key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_signature_method"]
    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_signature_method_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_signature_method value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_signature_method"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_callback_key(get_launch_args):
    """
    Does the launch request work with a missing oauth_callback key?
    It should, see https://www.imsglobal.org/specs/ltiv1p1/implementation-guide#toc-4.

    Note that some LMS do not add `oauth_callback` to the list of parameters.
    """
    validator, launch_url, headers, args = args_test_setup(
        get_launch_args, oauth_callback=None
    )

    assert validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_callback_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_callback value?
    """
    validator, launch_url, headers, args = args_test_setup(
        get_launch_args, oauth_callback=""
    )
    validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_version_key(get_launch_args):
    """
    Does the launch request work with a missing oauth_version key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_version"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_version_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_version value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_version"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_oauth_signature_key(get_launch_args):
    """
    Does the launch request work with a missing oauth_signature key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["oauth_signature"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_oauth_signature_value(
    get_launch_args,
):
    """
    Does the launch request work with an empty oauth_signature value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_signature"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_unregistered_consumer_key(get_launch_args):
    """
    Does the launch request work with a consumer key that does not match?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    args["oauth_consumer_key"] = "fake_consumer_key"

    with pytest.raises(HTTPError):
        assert validator.validate_launch_request(launch_url, headers, args)


def test_unregistered_shared_secret(get_launch_args):
    """
    Does the launch request work with a shared secret that does not match?
    """
    _, launch_url, headers, args = args_test_setup(get_launch_args)
    validator = LTI11LaunchValidator(
        {args["oauth_consumer_key"]: "my_other_shared_secret"}
    )
    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_lti_message_type(get_launch_args):
    """
    Does the launch request work with a missing lti_message_type argument?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["lti_message_type"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_lti_message_type(
    get_launch_args,
):
    """
    Does the launch request work with an empty lti_message_type value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["lti_message_type"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_lti_version(get_launch_args):
    """
    Does the launch request work with a missing oauth_signature key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["lti_version"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_lti_version(get_launch_args):
    """
    Does the launch request work with an empty oauth_signature value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["lti_version"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_resource_link_id(get_launch_args):
    """
    Does the launch request work with a missing resource_link_id key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["resource_link_id"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_resource_link_id(
    get_launch_args,
):
    """
    Does the launch request work with an empty resource_link_id value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["resource_link_id"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_missing_user_id_key(get_launch_args):
    """
    Does the launch request work with a missing user_id key?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)
    del args["user_id"]

    with pytest.raises(HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_empty_user_id_value(get_launch_args):
    """
    Does the launch request work with an empty user_id value?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["user_id"] = ""
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_same_oauth_timestamp_different_oauth_nonce(
    get_launch_args,
):
    """
    Does the launch request pass with when using a different nonce with the
    same timestamp?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_nonce"] = "fake_nonce"
        validator.validate_launch_request(launch_url, headers, args)


def test_launch_with_same_oauth_nonce_different_oauth_timestamp(
    get_launch_args,
):
    """
    Does the launch request pass with when using a different timestamp with the
    same nonce?
    """
    validator, launch_url, headers, args = args_test_setup(get_launch_args)

    with pytest.raises(HTTPError):
        args["oauth_timestamp"] = "0123456789"
        validator.validate_launch_request(launch_url, headers, args)
