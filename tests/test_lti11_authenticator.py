import pytest

from tornado import web

from ltiauthenticator.lti11.validator import LTI11LaunchValidator


def test_launch(make_lti11_basic_launch_request_args):
    """Test a basic launch request"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)


def test_wrong_key(make_lti11_basic_launch_request_args):
    """Test that the request is rejected when receiving the wrong consumer key."""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({"wrongkey": oauth_consumer_secret})

    with pytest.raises(web.HTTPError):
        assert validator.validate_launch_request(launch_url, headers, args)


def test_wrong_secret(make_lti11_basic_launch_request_args):
    """Test that a request is rejected when the signature is created with the wrong secret."""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: "wrongsecret"})

    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_full_replay(make_lti11_basic_launch_request_args):
    """Ensure that an oauth timestamp/nonce replay raises an HTTPError"""

    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_partial_replay_timestamp(make_lti11_basic_launch_request_args):
    """Test that a partial timestamp replay raises an HTTPError."""

    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["oauth_timestamp"] = str(int(float(args["oauth_timestamp"])) - 1)
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_partial_replay_nonce(make_lti11_basic_launch_request_args):
    """Test that a partial nonce replay raises an HTTPError"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["oauth_nonce"] = args["oauth_nonce"] + "1"
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)


def test_dubious_extra_args(make_lti11_basic_launch_request_args):
    """Ensure that dubious extra args are rejected"""
    oauth_consumer_key = "my_consumer_key"
    oauth_consumer_secret = "my_shared_secret"
    launch_url = "http://jupyterhub/hub/lti/launch"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    args = make_lti11_basic_launch_request_args(
        oauth_consumer_key,
        oauth_consumer_secret,
    )

    validator = LTI11LaunchValidator({oauth_consumer_key: oauth_consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args["extra_credential"] = "i have admin powers"
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)
