import time

from traitlets import Bool, Dict
from tornado import gen, web

from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join

from oauthlib.oauth1.rfc5849 import signature
from collections import OrderedDict


PROCESS_START_TIME = time.time()

nonces = OrderedDict()


class LTIAuthenticateHandler(BaseHandler):
    """
    Handler for /lti/launch

    Implements v1 of the LTI protocol for passing authentication information
    through.

    If there's a custom parameter called 'next', will redirect user to
    that URL after authentication. Else, will send them to /home.
    """

    @gen.coroutine
    def post(self):
        user = yield self.login_user()
        self.redirect(self.get_body_argument('custom_next', self.get_next_url()))


class LTIAuthenticator(Authenticator):
    """
    JupyterHub Authenticator for use with LTI based services (EdX, Canvas, etc)
    """

    auto_login = True
    login_service = 'LTI'

    consumers = Dict(
        {},
        config=True,
        help="""
        A dict of consumer keys mapped to consumer secrets for those keys.

        Allows multiple consumers to securely send users to this JupyterHub
        instance.
        """
    )

    def get_handlers(self, app):
        return [
            ('/lti/launch', LTIAuthenticateHandler)
        ]

    @gen.coroutine
    def authenticate(self, handler, data=None):
        # FIXME: Run a process that cleans up old nonces every other minute
        # Validate that we have a consumer key for this request
        consumer_key = handler.get_body_argument('oauth_consumer_key')
        if consumer_key not in self.consumers:
            # Be careful to not reflect the consumer_key here
            raise web.HTTPError(401, "Invalid oauth_consumer_key")


        # Convert args from dict to list of tuples that oauthlib wants
        args = []
        for key, values in handler.request.arguments.items():
            for value in values:
                args.append((key, value))
        base_string = signature.construct_base_string(
            'POST',
            signature.normalize_base_string_uri(handler.request.full_url()),
            signature.normalize_parameters(
                signature.collect_parameters(
                    body=args,
                    headers=handler.request.headers
                )
            )
        )

        consumer_secret = self.consumers[consumer_key]

        sign = signature.sign_hmac_sha1(base_string, consumer_secret, None)
        is_valid = signature.safe_string_equals(sign, handler.get_body_argument('oauth_signature'))

        if not is_valid:
            raise web.HTTPError(401, "Invalid oauth_signature")

        ts = int(handler.get_body_argument('oauth_timestamp'))
        nonce = handler.get_body_argument('oauth_nonce')
        # Allow 30s clock skew between LTI Consumer and Provider
        # Also don't accept timestamps from before our process started, since that could be
        # a replay attack - we won't have nonce lists from back then. This would allow users
        # who can control / know when our process restarts to trivially do replay attacks.
        if time.time() - ts > 30 or ts < PROCESS_START_TIME:
            raise web.HTTPError(401, "oauth_timestamp too old")

        if ts in nonces and nonce in nonces[ts]:
            raise web.HTTPError(401, "oauth_nonce + oauth_timestamp already used")

        nonces.setdefault(ts, set()).add(nonce)

        auth_state = {}
        for k, values in handler.request.arguments.items():
            if not k.startswith('oauth_'):
                auth_state[k] = values[0].decode() if len(values) == 1 else [v.decode() for v in values]

        print(auth_state)
        return {
            'name': handler.get_body_argument('user_id'),
            'auth_state': auth_state
        }

    def login_url(self, base_url):
        return url_path_join(base_url, '/lti/launch')
