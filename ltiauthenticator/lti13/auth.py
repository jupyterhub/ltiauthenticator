import logging
import os
from typing import Dict

from jupyterhub.app import JupyterHub
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from oauthenticator.oauth2 import OAuthenticator
from tornado.web import HTTPError
from traitlets.config import Unicode

from .handlers import LTI13CallbackHandler
from .handlers import LTI13ConfigHandler
from .handlers import LTI13LaunchValidator
from .handlers import LTI13LoginHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LTI13Authenticator(OAuthenticator):
    """
    JupyterHub LTI 1.3 Authenticator which extends the `OAuthenticator` class. (LTI 1.3
    is basically an extension of OIDC/OAuth2). Messages sent to this authenticator are sent
    from a LTI 1.3 Platform, such as an LMS. JupyterHub, as the authenticator, works as the
    LTI 1.3 External Tool. The basic login flow uses the authorization code grant type. As such,
    the client id is only required if the JupyterHub is configured to send information back to the
    LTI 1.3 Platform, in which case it would require the client credentials grant type.

    This class utilizes the following configurables defined in the `OAuthenticator` base class
    (all are required unless stated otherwise):

        - authorize_url
        - oauth_callback_url
        - token_url
        - (Optional) client_id

    Ref:
      - https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/oauth2.py
      - http://www.imsglobal.org/spec/lti/v1p3/
    """

    login_service = "LTI 1.3"

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    endpoint = Unicode(
        os.getenv("LTI13_ENDPOINT", ""),
        allow_none=False,
        config=True,
        help="""
        The platform's base endpoint used when redirecting requests to the platform
        after receiving the initial login request.
        """,
    )

    username_key = Unicode(
        "email",
        allow_none=False,
        config=True,
        help="""
        JWT claim present in LTI 1.3 login initiation flow used to set the user's JupyterHub's username.
        Some common examples include:

          - User's email address: email
          - Given name: given_name
        
        Your LMS (Canvas / Open EdX / Moodle / others) may provide additional keys in the
        LTI 1.3 login initiatino flow that you can use to set the username. In most cases these
        are located in the `https://purl.imsglobal.org/spec/lti/claim/custom` claim. You may also
        have the option of using variable substitutions to fetch values that aren't provided with
        your vendor's standard LTI 1.3 login initiation flow request. If your platform's LTI 1.3
        settings are defined with privacy enabled, then by default the `sub` claim is used to set the
        username.

        Reference the IMS LTI specification on variable substitutions:
        http://www.imsglobal.org/spec/lti/v1p3/#customproperty.
        """,
    )

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [
            ("/lti13/config", LTI13ConfigHandler),
        ]

    async def authenticate(  # noqa: C901
        self, handler: LTI13LoginHandler, data: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Overrides authenticate from base class to handle LTI 1.3 authentication requests.

        Args:
          handler: handler object
          data: authentication dictionary

        Returns:
          Authentication dictionary
        """
        validator = LTI13LaunchValidator()

        # get jwks endpoint and token to use as args to decode jwt.
        self.log.debug("JWKS platform endpoint is %s" % self.endpoint)
        id_token = handler.get_argument("id_token")

        # extract claims from jwt (id_token) sent by the platform. as tool use the jwks (public key)
        # to verify the jwt's signature.
        jwt_decoded = await validator.jwt_verify_and_decode(
            id_token, self.endpoint, False, audience=self.client_id
        )
        self.log.debug("Decoded JWT: %s" % jwt_decoded)

        if validator.validate_launch_request(jwt_decoded):
            username = jwt_decoded.get(self.username_key)
            self.log.debug(
                f"Username_key is {self.username_key} and value fetched from JWT is {username}"
            )
            if not username:
                if "sub" in jwt_decoded and jwt_decoded["sub"]:
                    username = jwt_decoded["sub"]
                else:
                    raise HTTPError(400, "Unable to set the username")

            self.log.debug("username is %s" % username)

            return {
                "name": username,
                "auth_state": {k: v for k, v in jwt_decoded.items()},  # noqa: E231
            }


class LocalLTI13Authenticator(LocalAuthenticator, OAuthenticator):
    """A version that mixes in local system user creation"""

    pass
