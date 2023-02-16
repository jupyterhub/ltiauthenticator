import logging
import os
from typing import Dict, List

from jupyterhub.app import JupyterHub
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join
from oauthenticator.oauth2 import OAuthenticator
from tornado.web import HTTPError
from traitlets.config import List as TraitletsList
from traitlets.config import Unicode

from .handlers import (
    LTI13CallbackHandler,
    LTI13ConfigHandler,
    LTI13LaunchValidator,
    LTI13LoginHandler,
)

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

    jwks_algorithms = TraitletsList(
        default_value=["RS256"],
        config=True,
        help="""
        The platform's base endpoint used when redirecting requests to the platform
        after receiving the initial login request.
        """,
    )

    # FIXME: This name and description is incorrect. It is practically used as
    #        reference to a platforms JWKS endpoint.
    #
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

    tool_name = Unicode(
        "JupyterHub",
        config=True,
        help="""
        Name of tool provided to the LMS when installed via the config URL.

        This is primarily used for display purposes.
        """,
    )

    tool_description = Unicode(
        "Launch interactive Jupyter Notebooks with JupyterHub",
        config=True,
        help="""
        Description of tool provided to the LMS when installed via the config URL.

        This is primarily used for display purposes.
        """,
    )

    def login_url(self, base_url):
        return url_path_join(base_url, "lti13", "oauth_login")

    def get_handlers(self, app: JupyterHub) -> List[BaseHandler]:
        return [
            (r"/lti13/oauth_login", self.login_handler),
            (r"/lti13/oauth_callback", self.callback_handler),
            (r"/lti13/config", LTI13ConfigHandler),
        ]

    async def authenticate(
        self, handler: LTI13LoginHandler, data: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Overrides authenticate from the OAuthenticator base class to handle LTI
        1.3 authentication requests based on a passed JWT. The JWT is verified
        to be signed by the LTI 1.3 platform via a JWKs endpoint it should
        expose.

        Args:
          handler: handler object
          data: authentication dictionary

        Returns:
          Authentication dictionary
        """
        id_token = handler.get_argument("id_token")

        validator = LTI13LaunchValidator()
        jwt_decoded = validator.verify_and_decode_jwt(
            id_token,
            audience=self.client_id,
            jwks_endpoint=self.endpoint,
            jwks_algorithms=self.jwks_algorithms,
        )
        validator.validate_launch_request(jwt_decoded)

        username = jwt_decoded.get(self.username_key)
        if not username:
            if jwt_decoded.get("sub"):
                username = jwt_decoded["sub"]
            else:
                raise HTTPError(
                    400,
                    f"Unable to set the username with username_key {self.username_key}",
                )

        return {
            "name": username,
            "auth_state": jwt_decoded,
        }


class LocalLTI13Authenticator(LocalAuthenticator, OAuthenticator):
    """A version that mixes in local system user creation"""

    pass
