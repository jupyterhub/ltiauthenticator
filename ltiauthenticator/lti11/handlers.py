from jupyterhub.handlers import BaseHandler
from tornado import gen

from .templates import LTI11_CONFIG_TEMPLATE
from ..utils import get_client_protocol


class LTI11AuthenticateHandler(BaseHandler):
    """
    Handler for the LTI11Authenticator's launch_url_path config.

    Implements v1.1 of the LTI protocol for passing authentication information
    through.

    If there's a custom parameter called 'next', will redirect user to
    that URL after authentication. Else, will send them to /home.
    """

    def set_login_cookie(self, user):
        super().set_login_cookie(user)

        # Make sure that hub cookie is always set, even if the user was already logged in
        self.set_hub_cookie(user)

    @gen.coroutine
    def post(self):
        """
        Technical reference of relevance to understand this function
        ------------------------------------------------------------
        1. Class dependencies
           - jupyterhub.handlers.BaseHandler: https://github.com/jupyterhub/jupyterhub/blob/abb93ad799865a4b27f677e126ab917241e1af72/jupyterhub/handlers/base.py#L69
           - tornado.web.RequestHandler: https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler
        2. Function dependencies
           - login_user: https://github.com/jupyterhub/jupyterhub/blob/abb93ad799865a4b27f677e126ab917241e1af72/jupyterhub/handlers/base.py#L696-L715
             login_user is defined in the JupyterHub wide BaseHandler class,
             mainly wraps a call to the authenticate function and follow up.
             a successful authentication with a call to auth_to_user that
             persists a JupyterHub user and returns it.
           - get_next_url: https://github.com/jupyterhub/jupyterhub/blob/abb93ad799865a4b27f677e126ab917241e1af72/jupyterhub/handlers/base.py#L587
           - get_body_argument: https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.get_body_argument
        """
        # FIXME: Figure out if we want to pass the user returned from
        #        self.login_user() to self.get_next_url(). It is named
        #        _ for now as pyflakes is fine about having an unused
        #        variable named _.
        _ = yield self.login_user()
        next_url = self.get_next_url()
        body_argument = self.get_body_argument(
            name="custom_next",
            default=next_url,
        )

        self.redirect(body_argument)


class LTI11ConfigHandler(BaseHandler):
    """
    Renders XML configuration file for LTI 1.1
    """

    title = Unicode(
        default_value="JupyterHub",
        config=True,
        help="""
        The tool's title.
        """,
    )

    description = Unicode(
        default_value="canvas.instructure.com",
        config=True,
        help="""
        The tool's description.
        """,
    )

    icon = Unicode(
        default_value="canvas.instructure.com",
        config=True,
        help="""
        The icon used to represent the tool. This icon is usually displayed in the LTI 1.1 consumer interface.
        """,
    )

    async def get(self) -> None:
        """
        Gets the XML config which is used by LTI consumers to install the external tool.

        - The extensions key contains settings for specific vendors, such as canvas,
        moodle, edx, among others.
        - The tool uses public settings by default. Users that wish to install the tool with
        private settings should either copy/paste the json or toggle the application to private
        after it is installed with the platform.
        - Usernames are obtained by first attempting to get and normalize values sent when
        tools are installed with public settings. If private, the username is set using the
        anonumized user data when requests are sent with private installation settings.
        """
        self.set_header("Content-Type", "application/json")

        # get the origin protocol
        protocol = get_client_protocol(self)
        # build the configuration XML
        config_xml = LTI11_CONFIG_TEMPLATE.format(
            description=self.description,
            icon=self.icon,
            launch_url=f"{protocol}://{self.request.host}{self.request.uri}",
            title=self.title,
        )

        self.write(config_xml)
