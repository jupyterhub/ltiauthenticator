import time
import pytest
from tornado import web
from ltiauthenticator import LTILaunchValidator
from oauthlib.oauth1.rfc5849 import signature

def make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
):
    args = {
        'oauth_consumer_key': consumer_key,
        'oauth_timestamp': str(oauth_timestamp),
        'oauth_nonce': oauth_nonce
    }

    args.update(extra_args)

    base_string = signature.signature_base_string(
        'POST',
        signature.base_string_uri(launch_url),
        signature.normalize_parameters(
            signature.collect_parameters(body=args, headers={})
        )
    )

    args['oauth_signature'] = signature.sign_hmac_sha1(base_string, consumer_secret, None)

    return args

def test_launch():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

def test_wrong_key():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({'wrongkey': consumer_secret})

    with pytest.raises(web.HTTPError):
        assert validator.validate_launch_request(launch_url, headers, args)

def test_wrong_secret():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: 'wrongsecret'})

    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)

def test_full_replay():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)

def test_partial_replay_timestamp():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args['oauth_timestamp'] = str(int(float(args['oauth_timestamp'])) - 1)
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)

def test_partial_replay_nonce():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args['oauth_nonce'] = args['oauth_nonce'] + "1"
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)

def test_dubious_extra_args():
    consumer_key = 'key1'
    consumer_secret = 'secret1'
    launch_url = 'http://localhost:8000/hub/lti/launch'
    headers = {}
    oauth_timestamp = time.time()
    oauth_nonce = str(time.time())
    extra_args = {
        'arg1': 'value1'
    }

    args = make_args(
        consumer_key, consumer_secret,
        launch_url, oauth_timestamp, oauth_nonce, extra_args
    )

    validator = LTILaunchValidator({consumer_key: consumer_secret})

    assert validator.validate_launch_request(launch_url, headers, args)

    args['extra_credential'] = 'i have admin powers'
    with pytest.raises(web.HTTPError):
        validator.validate_launch_request(launch_url, headers, args)
