import pytest
from jupyterhub.app import JupyterHub
from traitlets.config import Config


@pytest.fixture
def app() -> JupyterHub:
    """Creates an instance of the JupyterHub application.

    Returns:
        MockHub: a mocked JupyterHub instance.
    """

    def _app(cfg: Config) -> JupyterHub:
        hub = JupyterHub(config=cfg)
        hub.tornado_settings = {"foo": "bar"}
        hub.init_hub()
        hub.base_url = "/mytenant"
        return hub

    return _app
