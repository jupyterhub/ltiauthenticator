from jupyterhub.app import JupyterHub
from jupyterhub.handlers import BaseHandler

from ltiauthenticator.lti13.auth import LTI13Authenticator
from ltiauthenticator.lti13.handlers import LTI13ConfigHandler


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
