import secrets
import time

from oauthlib.oauth1.rfc5849 import signature

import pytest

from typing import Dict


@pytest.fixture(scope="function")
def make_lti11_basic_launch_request_args() -> Dict[str, str]:
    def _make_lti11_basic_launch_args(
        oauth_consumer_key: str = "my_consumer_key",
        oauth_consumer_secret: str = "my_shared_secret",
    ):
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = secrets.token_urlsafe(32)
        args = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0".encode(),
            "resource_link_id": "88391-e1919-bb3456",
            "oauth_consumer_key": oauth_consumer_key,
            "oauth_timestamp": str(int(oauth_timestamp)),
            "oauth_nonce": str(oauth_nonce),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_callback": "about:blank",
            "oauth_version": "1.0",
            "user_id": "123123123",
        }
        extra_args = {"my_key": "this_value"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        launch_url = "http://jupyterhub/hub/lti/launch"

        args.update(extra_args)

        base_string = signature.signature_base_string(
            "POST",
            signature.base_string_uri(launch_url),
            signature.normalize_parameters(
                signature.collect_parameters(body=args, headers=headers)
            ),
        )

        args["oauth_signature"] = signature.sign_hmac_sha1(
            base_string, oauth_consumer_secret, None
        )
        return args

    return _make_lti11_basic_launch_args
