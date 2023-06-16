import logging
from typing import Any, Dict, List

from jupyterhub.app import JupyterHub  # type: ignore
from jupyterhub.auth import Authenticator  # type: ignore
from jupyterhub.handlers import BaseHandler  # type: ignore
from jupyterhub.utils import url_path_join  # type: ignore
from traitlets import CaselessStrEnum
from traitlets import List as TraitletsList
from traitlets import Set as TraitletsSet
from traitlets import Unicode

from ..utils import get_browser_protocol
from .constants import LTI13_CUSTOM_CLAIM
from .error import LoginError
from .handlers import LTI13CallbackHandler, LTI13ConfigHandler, LTI13LoginInitHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LTI13Authenticator(Authenticator):
    """
    JupyterHub LTI 1.3 Authenticator. LTI 1.3 is basically an extension of OIDC/OAuth2.
    Messages sent to this authenticator are sent from a LTI 1.3 Platform, such as an LMS.
    JupyterHub, as the authenticator, works as the LTI 1.3 External Tool.
    The basic login flow is authentication using the implicit flow.
    As such, at least one client id is required.

    Ref:
      - http://www.imsglobal.org/spec/lti/v1p3/
      - https://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth
    """

    login_service = "LTI 1.3"

    # handlers used for login, callback, and json config endpoints
    login_handler = LTI13LoginInitHandler
    callback_handler = LTI13CallbackHandler
    config_handler = LTI13ConfigHandler

    authorize_url = Unicode(
        config=True,
        help="""Authorization end-point of the platforms identity provider.""",
    )

    client_id = TraitletsSet(
        trait=Unicode(),
        config=True,
        help="""
        The client ID or a list of client IDs identifying the JuyterHub within the LMS platform.
        Must contain the client IDs created when registering the tool on the LMS platform.

        Possible values are of type str or iterables thereof.
        """,
    )

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

    uri_scheme = CaselessStrEnum(
        ("auto", "https", "http"),
        default_value="auto",
        config=True,
        help="""
        Scheme to use for endpoint URLs offered by this authenticator.

        Possible values are "auto", "https" and "http", where "auto" is the default.
        When "auto" is chosen, the scheme is inferred from the incomming request's header.
        Since this may lead to unreliable results in some deployment scenarios (in particular
        when several different versions of forwarding headers are mixed), manually specifying it
        here is kept as an escape hatch.
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
            (self.config_json_url(""), self.config_handler),
        ]

    async def authenticate(
        self, handler: LTI13LoginInitHandler, data: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Handles LTI 1.3 launch requests based on a passed JWT.

        Args:
          handler: handler object
          data: authentication dictionary. The decoded, verified and validated id_token send by the platform

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

    def get_uri_scheme(self, request) -> str:
        """Return scheme to use for endpoint URLs of this authenticator."""
        if self.uri_scheme == "auto":
            return get_browser_protocol(request)
        # manually specified https or http
        return self.uri_scheme
