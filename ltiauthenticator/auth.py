from traitlets import Bool, Dict
from tornado import gen, web

from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join

from .validator import LTILaunchValidator, LTILaunchValidationError

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
        validator = LTILaunchValidator(self.consumers)

        args = {}
        for k, values in handler.request.body_arguments.items():
            args[k] = values[0].decode() if len(values) == 1 else [v.decode() for v in values]


        try:
            if validator.validate_launch_request(
                    handler.request.full_url(),
                    handler.request.headers,
                    args
            ):
                return {
                    'name': handler.get_body_argument('user_id'),
                    'auth_state': {k: v for k, v in args.items() if not k.startswith('oauth_')}
                }
        except LTILaunchValidationError as e:
            raise web.HTTPError(401, e.message)


    def login_url(self, base_url):
        return url_path_join(base_url, '/lti/launch')


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
