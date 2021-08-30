import time
from collections import OrderedDict
from typing import Any
from typing import Dict

from oauthlib.oauth1.rfc5849 import signature
from tornado.web import HTTPError
from traitlets.config import LoggingConfigurable

from .constants import LTI11_LAUNCH_PARAMS_REQUIRED
from .constants import LTI11_OAUTH_ARGS


class LTI11LaunchValidator(LoggingConfigurable):
    """
    This class closely mimics the jupyterhub/ltiauthenticator LTILaunchValidator
    base class. Inherits from the LoggingConfigurable traitlet to support logging.

    Allows JupyterHub to verify LTI 1.1 compatible requests as a tool
    provider (TP).

    For an instance of this class to work, you need to set the consumer key and
    shared secret key(s)/value(s) in `LTI11Authenticator` settings, which inherits
    from the ``ltiauthenticator.LTIAuthenticator`` class. The key/value pairs are
    set as are defined as a dict using the ``consumers`` attribute.

    Attributes:
      consumers: consumer key and shared secret key/value pair(s)
    """

    # Keep a class-wide, global list of nonces so we can detect & reject
    # replay attacks. This possibly makes this non-threadsafe, however.
    nonces = OrderedDict()

    def __init__(self, consumers):
        self.consumers = consumers

    def validate_launch_request(
        self,
        launch_url: str,
        headers: Dict[str, Any],
        args: Dict[str, Any],
    ) -> bool:
        """
        Validate a given LTI 1.1 launch request. The arguments' k/v's are either
        required, recommended, or optional. The required/recommended/optional
        keys are defined as constants.

        Args:
          launch_url: URL (base_url + path) that receives the launch request,
            usually from a tool consumer.
          headers: HTTP headers included with the POST request
          args: the body sent to the launch url.

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required argument is not inclued in the POST request.
        """
        # Ensure that required oauth_* body arguments are included in the request
        for param in LTI11_OAUTH_ARGS:
            if param not in args.keys():
                raise HTTPError(
                    400, "Required oauth arg %s not included in request" % param
                )
            if not args.get(param):
                raise HTTPError(
                    400, "Required oauth arg %s does not have a value" % param
                )

        # Ensure that consumer key is registered in in jupyterhub_config.py
        # LTI11Authenticator.consumers defined in parent class
        if args["oauth_consumer_key"] not in self.consumers:
            raise HTTPError(401, "unknown oauth_consumer_key")

        # Ensure that required LTI 1.1 body arguments are included in the request
        for param in LTI11_LAUNCH_PARAMS_REQUIRED:
            if param not in args.keys():
                raise HTTPError(
                    400, "Required LTI 1.1 arg arg %s not included in request" % param
                )
            if not args.get(param):
                raise HTTPError(
                    400, "Required LTI 1.1 arg %s does not have a value" % param
                )

        # Inspiration to validate nonces/timestamps from OAuthlib
        # https://github.com/oauthlib/oauthlib/blob/HEAD/oauthlib/oauth1/rfc5849/endpoints/base.py#L147
        if len(str(int(args["oauth_timestamp"]))) != 10:
            raise HTTPError(401, "Invalid timestamp format.")
        try:
            ts = int(args["oauth_timestamp"])
        except ValueError:
            raise HTTPError(401, "Timestamp must be an integer.")
        else:
            # Reject timestamps that are older than 30 seconds
            if abs(time.time() - ts) > 30:
                raise HTTPError(
                    401,
                    "Timestamp given is invalid, differ from "
                    "allowed by over %s seconds." % str(int(time.time() - ts)),
                )
            if (
                ts in LTI11LaunchValidator.nonces
                and args["oauth_nonce"] in LTI11LaunchValidator.nonces[ts]
            ):
                raise HTTPError(401, "oauth_nonce + oauth_timestamp already used")
            LTI11LaunchValidator.nonces.setdefault(ts, set()).add(args["oauth_nonce"])

        # convert arguments dict back to a list of tuples for signature
        args_list = [(k, v) for k, v in args.items()]

        base_string = signature.signature_base_string(
            "POST",
            signature.base_string_uri(launch_url),
            signature.normalize_parameters(
                signature.collect_parameters(body=args_list, headers=headers)
            ),
        )
        consumer_secret = self.consumers[args["oauth_consumer_key"]]
        sign = signature.sign_hmac_sha1(base_string, consumer_secret, None)
        is_valid = signature.safe_string_equals(sign, args["oauth_signature"])
        self.log.debug("signature in request: %s" % args["oauth_signature"])
        self.log.debug("calculated signature: %s" % sign)
        if not is_valid:
            raise HTTPError(401, "Invalid oauth_signature")

        return True
