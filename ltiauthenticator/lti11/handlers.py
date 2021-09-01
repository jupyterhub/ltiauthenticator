from jupyterhub.handlers import BaseHandler
from tornado import gen

from ..utils import get_client_protocol
from .templates import LTI11_CONFIG_TEMPLATE


class LTI11AuthenticateHandler(BaseHandler):
    """
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
    Renders LTI 1.1 configuration file in XML format. Having the external tool's
    settings available with a configuration URL with the standard LTI 1.1 XML format
    allows users to use the URL and/or Paste XML options when defining the external
    tool settings within a a tool consumer, such as a Learning Management System (LMS).

    This configuration option is also known as Defining an LTI Link for a Tool Consumer.

    ref: http://www.imsglobal.org/specs/lti/xml
    """

    def get(self) -> None:
        """
        Renders the XML config which is used by LTI consumers to install the external tool.
        """
        self.set_header("Content-Type", "application/xml")

        # get the launch url from the client request
        protocol = get_client_protocol(self)
        launch_url = f"{protocol}://{self.request.host}{self.application.settings['base_url']}hub/lti/launch"
        self.log.debug(f"Calculated launch URL is: {launch_url}")

        # build the configuration XML
        config_xml = LTI11_CONFIG_TEMPLATE.format(
            description=self.authenticator.config_description,
            icon=self.authenticator.config_icon,
            launch_url=launch_url,
            title=self.authenticator.config_title,
        )

        self.write(config_xml)
