from jupyterhub.app import JupyterHub
from jupyterhub.handlers import BaseHandler

from ltiauthenticator.lti11.auth import LTI11Authenticator
from ltiauthenticator.lti11.handlers import LTI11AuthenticateHandler
from ltiauthenticator.lti11.handlers import LTI11ConfigHandler
from ltiauthenticator.lti13.auth import LTI13Authenticator
from ltiauthenticator.lti13.handlers import LTI13ConfigHandler


class MockLTI11Authenticator(LTI11Authenticator):
    """Mocks the LTI11Authenticator for testing.

    Args:
        LTI11Authenticator (Authenticator): The LTI11Authenticator used for mocking.
    """

    auto_login = True
    config_description = "My LTI 1.1 description"
    config_icon = "http://my.icon.url"
    config_title = "LTI 1.1 configuration"
    config_url = "/lti11/config"
    consumers = {"consumer_key": "myconsumerkey", "shared_secret": "mysharedsecret"}
    launch_url = "/lti/launch"
    login_service = "LTI 1.1"
    username_key = "custom_canvas_user_id"

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [
            (f"{self.launch_url}", LTI11AuthenticateHandler),
            (f"{self.config_url}", LTI11ConfigHandler),
        ]


class MockLTI13Authenticator(LTI13Authenticator):
    """Mocks the LTI13Authenticator for testing.

    Args:
        LTI13Authenticator (OAuthenticator): The LTI13Authenticator used for mocking.
    """

    auto_login = True
    login_service = "LTI 1.3"
    username_key = "email"
    client_id = "abc123"
    config_url = "/lti13/config"
    authorize_url = "https://my.platform.domain/api/lti/authorize_redirect"
    endpoint = "https://my.platform.domain"
    token_url = "https://my.platform.domain/login/oauth2/token"

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [
            (f"{self.config_url}", LTI13ConfigHandler),
        ]
