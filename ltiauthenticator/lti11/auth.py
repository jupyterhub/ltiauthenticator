from jupyterhub.app import JupyterHub
from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join

from traitlets.config import Dict
from traitlets.config import Unicode

from ltiauthenticator.lti11.handlers import LTI11AuthenticateHandler
from ltiauthenticator.lti11.validator import LTI11LaunchValidator
from ltiauthenticator.utils import convert_request_to_dict
from ltiauthenticator.utils import get_client_protocol


class LTI11Authenticator(Authenticator):
    """
    JupyterHub LTI 1.1 Authenticator which extends the ltiauthenticator.LTIAuthenticator class.
    Messages sent to this authenticator are sent from a tool consumer (TC), such as
    an LMS. JupyterHub, as the authenticator, works as the tool provider (TP), also
    known as the external tool.

    The LTIAuthenticator base class defines the consumers, defined as 1 or (n) consumer key
    and shared secret k/v's to verify requests from their tool consumer.
    """

    auto_login = True
    login_service = "LTI 1.1"

    consumers = Dict(
        {},
        config=True,
        help="""
        A dict of consumer keys mapped to consumer secrets for those keys.
        Allows multiple consumers to securely send users to this JupyterHub
        instance.
        """,
    )

    username_key = Unicode(
        None,
        allow_none=True,
        config=True,
        help="""
        Key present in LTI 1.1 launch request used to set the user's JupyterHub's username.
        Common standard (vendor agnostic) options are:
          - User's email address: lis_person_contact_email_primary
          - Opaque user id: user_id
        Your LMS (Canvas / Open EdX / Moodle / others) may provide additional
        keys in the LTI 1.1 launch request that you can use to set the username. In most cases these
        are prefixed with `custom_`.
        When the default of 'None' is set, the following backwards compatible behavior is provided:
          If `canvas_custom_user_id` is present, that is used. Otherwise,
          the anonymized `user_id` is used.
        """,
    )

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [("/lti/launch", LTI11AuthenticateHandler)]

    def login_url(self, base_url):
        return url_path_join(base_url, "/lti/launch")

    async def authenticate(  # noqa: C901
        self, handler: BaseHandler, data: dict = None
    ) -> dict:  # noqa: C901
        """
        LTI 1.1 Authenticator. One or more consumer keys/values must be set in the jupyterhub config with the
        LTI11Authenticator.consumers dict.

        Args:
            handler: JupyterHub's Authenticator handler object. For LTI 1.1 requests, the handler is
              an instance of LTIAuthenticateHandler.
            data: optional data object

        Returns:
            Authentication dictionary

        Raises:
            HTTPError if the required values are not in the request
        """
        validator = LTI11LaunchValidator(self.consumers)

        self.log.debug(
            "Original arguments received in request: %s" % handler.request.arguments
        )

        # extract the request arguments to a dict
        args = convert_request_to_dict(handler.request.arguments)
        self.log.debug("Decoded args from request: %s" % args)

        # get the origin protocol
        protocol = get_client_protocol(handler)
        self.log.debug("Origin protocol is: %s" % protocol)

        # build the full launch url value required for oauth1 signatures
        launch_url = f"{protocol}://{handler.request.host}{handler.request.uri}"
        self.log.debug("Launch url is: %s" % launch_url)

        if validator.validate_launch_request(launch_url, handler.request.headers, args):
            username = ""
            if self.username_key in args and args[self.username_key]:
                username = args[self.username_key]
            elif "custom_canvas_user_id" in args and args["custom_canvas_user_id"]:
                username = args["custom_canvas_user_id"]
            else:
                username = args["user_id"]

            return {
                "name": username,
                "auth_state": {
                    k: v for k, v in args.items() if not k.startswith("oauth_")
                },
            }
