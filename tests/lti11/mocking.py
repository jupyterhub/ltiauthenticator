from jupyterhub.app import JupyterHub  # type: ignore
from jupyterhub.handlers import BaseHandler  # type: ignore
from traitlets import Dict, Unicode

from ltiauthenticator.lti11.auth import LTI11Authenticator
from ltiauthenticator.lti11.handlers import LTI11AuthenticateHandler, LTI11ConfigHandler


class MockLTI11Authenticator(LTI11Authenticator):
    """Mocks the LTI11Authenticator for testing.

    Args:
        LTI11Authenticator (Authenticator): The LTI11Authenticator used for mocking.
    """

    auto_login = True
    config_description = Unicode("My LTI 1.1 description")
    config_icon = Unicode("http://my.icon.url")
    config_title = Unicode("LTI 1.1 configuration")
    config_url = "/lti11/config"
    consumers = Dict(
        {"consumer_key": "myconsumerkey", "shared_secret": "mysharedsecret"}
    )
    launch_url = "/lti/launch"
    login_service = "LTI 1.1"
    username_key = Unicode("custom_canvas_user_id")

    def get_handlers(self, app: JupyterHub) -> BaseHandler:
        return [
            (f"{self.launch_url}", LTI11AuthenticateHandler),
            (f"{self.config_url}", LTI11ConfigHandler),
        ]
