import logging
from typing import Any, Dict, List

from jupyterhub.app import JupyterHub
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join
from oauthenticator.oauth2 import OAuthenticator
from traitlets import List as TraitletsList
from traitlets import Unicode

from .constants import LTI13_CUSTOM_CLAIM
from .error import LoginError
from .handlers import LTI13CallbackHandler, LTI13ConfigHandler, LTI13LoginInitHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LTI13Authenticator(OAuthenticator):
    """
    JupyterHub LTI 1.3 Authenticator which extends the `OAuthenticator` class. (LTI 1.3
    is basically an extension of OIDC/OAuth2). Messages sent to this authenticator are sent
    from a LTI 1.3 Platform, such as an LMS. JupyterHub, as the authenticator, works as the
    LTI 1.3 External Tool. The basic login flow is authentication using the implicit flow. As such,
    the client id is always required.

    This class utilizes the following required configurables defined in the `OAuthenticator` base class:

        - authorize_url
        - client_id

    Ref:
      - https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/oauth2.py
      - http://www.imsglobal.org/spec/lti/v1p3/
      - https://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth
    """

    login_service = "LTI 1.3"

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginInitHandler
    callback_handler = LTI13CallbackHandler

    jwks_algorithms = TraitletsList(
        default_value=["RS256"],
        config=True,
        help="""
        Supported algorithms for signing JWT. The actual algorithm is declared by the authenticator
        in the `id_token_signed_response_alg` parameter during out-of-band registration.

        References:
        https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation
        """,
    )

    issuer = Unicode(
        allow_none=False,
        config=True,
        help="""
        The platform's issuer identifier. It is a case-sensitive URL, using the HTTPS
        scheme, that contains scheme, host, and optionally, port number, and path components,
        and no query or fragment components. It is provided by the platform.
        """,
    )

    jwks_endpoint = Unicode(
        allow_none=False,
        config=True,
        help="""
        The platform's JWKS endpoint used to obtain it's JSON Web Key Set to validate JWT signatures.
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
        LTI 1.3 login initiation flow that you can use to set the username. In most cases these
        are located in the `https://purl.imsglobal.org/spec/lti/claim/custom` claim. In this case,
        `username_key` must be prefixed with "custom_". For example, `username_key` value "custom_uname"
        will set the username to the value of the parameter `uname` within the
        `https://purl.imsglobal.org/spec/lti/claim/custom` claim.
        
        If your platform's LTI 1.3 settings are defined with privacy enabled, then by default the `sub`
        claim is used to set the username.
        
        You may also have the option of using variable substitutions to fetch values that aren't provided with
        your vendor's standard LTI 1.3 login initiation flow request.

        Reference to the IMS LTI specification on variable substitutions:
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

    def callback_url(self, base_url):
        return url_path_join(base_url, "lti13", "oauth_callback")

    def config_json_url(self, base_url):
        return url_path_join(base_url, "lti13", "config")

    def get_handlers(self, app: JupyterHub) -> List[BaseHandler]:
        return [
            (self.login_url(""), self.login_handler),
            (self.callback_url(""), self.callback_handler),
            (self.config_json_url(""), LTI13ConfigHandler),
        ]

    async def authenticate(
        self, handler: LTI13LoginInitHandler, data: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Overrides authenticate from the OAuthenticator base class to handle LTI
        1.3 launch requests based on a passed JWT.

        Args:
          handler: handler object
          data: authentication dictionary. The decoded, verified and validated id_token send by tehe platform

        Returns:
          Authentication dictionary
        """
        if not data:
            data = {}

        username = self.get_username(data)

        return {
            "name": username,
            "auth_state": data,
        }

    def get_username(self, token: Dict[str, Any]) -> str:
        """
        Infer the username from the ID token.

        If username_key begins with "custom_", that part will be removed and the key will
        be looked up inside the custom claim of the ID token.
        """
        data = token
        username_key = self.username_key

        if not username_key:
            username_key = "sub"

        if username_key.startswith("custom_"):
            data = token.get(LTI13_CUSTOM_CLAIM, {})
            # when dropping support for Python 3.8 we can replace the following by `username_key.removeprefix`
            username_key = username_key[len("custom_") :]

        username = data.get(username_key)
        if not username:
            logger.warning(
                f"Cannot find the key {username_key} in the ID token. `sub` used instread."
            )
            username = token.get("sub")
        if not username:
            raise LoginError(
                f"Unable to set the username with username_key {username_key}"
            )
        return username


class LocalLTI13Authenticator(LocalAuthenticator, OAuthenticator):
    """A version that mixes in local system user creation"""

    pass
