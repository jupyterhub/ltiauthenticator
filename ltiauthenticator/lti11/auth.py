from tornado import gen

from traitlets import Dict

from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join

from ltiauthenticator.lti11.handlers import LTIAuthenticateHandler
from ltiauthenticator.lti11.validator import LTILaunchValidator


class LTIAuthenticator(Authenticator):
    """
    JupyterHub Authenticator for use with LTI based services (EdX, Canvas, etc)
    """

    auto_login = True
    login_service = "LTI"

    consumers = Dict(
        {},
        config=True,
        help="""
        A dict of consumer keys mapped to consumer secrets for those keys.

        Allows multiple consumers to securely send users to this JupyterHub
        instance.
        """,
    )

    def get_handlers(self, app):
        return [("/lti/launch", LTIAuthenticateHandler)]

    @gen.coroutine
    def authenticate(self, handler, data) -> dict:
        # FIXME: Run a process that cleans up old nonces every other minute
        validator = LTILaunchValidator(self.consumers)

        args = {}
        for k, values in handler.request.body_arguments.items():
            args[k] = (
                values[0].decode() if len(values) == 1 else [v.decode() for v in values]
            )

        # handle multiple layers of proxied protocol (comma separated) and take the outermost
        # value (first from the list)
        if "x-forwarded-proto" in handler.request.headers:
            # x-forwarded-proto might contain comma delimited values
            # left-most value is the one sent by original client
            hops = [
                h.strip()
                for h in handler.request.headers["x-forwarded-proto"].split(",")
            ]
            protocol = hops[0]
        else:
            protocol = handler.request.protocol

        launch_url = protocol + "://" + handler.request.host + handler.request.uri

        if validator.validate_launch_request(launch_url, handler.request.headers, args):
            # Before we return lti_user_id, check to see if a canvas_custom_user_id was sent.
            # If so, this indicates two things:
            # 1. The request was sent from Canvas, not edX
            # 2. The request was sent from a Canvas course not running in anonymous mode
            # If this is the case we want to use the canvas ID to allow grade returns through the Canvas API
            # If Canvas is running in anonymous mode, we'll still want the 'user_id' (which is the `lti_user_id``)

            canvas_id = handler.get_body_argument("custom_canvas_user_id", default=None)

            if canvas_id is not None:
                user_id = handler.get_body_argument("custom_canvas_user_id")
            else:
                user_id = handler.get_body_argument("user_id")

            return {
                "name": user_id,
                "auth_state": {
                    k: v for k, v in args.items() if not k.startswith("oauth_")
                },
            }

    def login_url(self, base_url):
        return url_path_join(base_url, "/lti/launch")
