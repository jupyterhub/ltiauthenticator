from .mocking import MockLTI13Authenticator


async def test_lti_13_handler_paths(app):
    """Test if all handlers are correctly set with the LTI13Authenticator."""
    auth = MockLTI13Authenticator()
    handlers = auth.get_handlers(app)
    assert handlers[0][0] == "/lti13/config"
