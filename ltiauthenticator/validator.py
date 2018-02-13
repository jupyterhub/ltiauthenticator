import time

from oauthlib.oauth1.rfc5849 import signature
from collections import OrderedDict


class LTILaunchValidationError(Exception):
    def __init__(self, message):
        self.message = message


class LTILaunchValidator:
    # Record time when process starts, so we can reject requests made
    # before this
    PROCESS_START_TIME = int(time.time())

    # Keep a class-wide, global list of nonces so we can detect & reject
    # replay attacks. This possibly makes this non-threadsafe, however.
    nonces = OrderedDict()

    def __init__(self, consumers):
        self.consumers = consumers

    def validate_launch_request(
            self,
            launch_url,
            headers,
            args
    ):
        """
        Validate a given launch request

        launch_url: Full URL that the launch request was POSTed to
        headers: k/v pair of HTTP headers coming in with the POST
        args: dictionary of body arguments passed to the launch_url
            Must have the following keys to be valid:
                oauth_consumer_key, oauth_timestamp, oauth_nonce,
                oauth_signature
        """

        # Validate args!
        if 'oauth_consumer_key' not in args:
            raise LTILaunchValidationError("oauth_consumer_key missing")
        if args['oauth_consumer_key'] not in self.consumers:
            raise LTILaunchValidationError("oauth_consumer_key not known")

        if 'oauth_signature' not in args:
            raise LTILaunchValidationError("oauth_signature missing")
        if 'oauth_timestamp' not in args:
            raise LTILaunchValidationError('oauth_timestamp missing')

        # Allow 30s clock skew between LTI Consumer and Provider
        # Also don't accept timestamps from before our process started, since that could be
        # a replay attack - we won't have nonce lists from back then. This would allow users
        # who can control / know when our process restarts to trivially do replay attacks.
        oauth_timestamp = int(float(args['oauth_timestamp']))
        if (
                int(time.time()) - oauth_timestamp > 30
                or oauth_timestamp < LTILaunchValidator.PROCESS_START_TIME
        ):
            raise LTILaunchValidationError("oauth_timestamp too old")

        if 'oauth_nonce' not in args:
            raise LTILaunchValidationError('oauth_nonce missing')
        if (
                oauth_timestamp in LTILaunchValidator.nonces
                and args['oauth_nonce'] in LTILaunchValidator.nonces[oauth_timestamp]
        ):
            raise LTILaunchValidationError("oauth_nonce + oauth_timestamp already used")
        LTILaunchValidator.nonces.setdefault(oauth_timestamp, set()).add(args['oauth_nonce'])


        args_list = []
        for key, values in args.items():
            if type(values) is list:
                args_list += [(key, value) for value in values]
            else:
                args_list.append((key, values))

        base_string = signature.construct_base_string(
            'POST',
            signature.normalize_base_string_uri(launch_url),
            signature.normalize_parameters(
                signature.collect_parameters(body=args_list, headers=headers)
            )
        )

        consumer_secret = self.consumers[args['oauth_consumer_key']]

        sign = signature.sign_hmac_sha1(base_string, consumer_secret, None)
        is_valid = signature.safe_string_equals(sign, args['oauth_signature'])

        if not is_valid:
            raise LTILaunchValidationError("Invalid oauth_signature")

        return True