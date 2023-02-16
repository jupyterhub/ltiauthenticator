from .mocking import MockLTI13Authenticator


async def test_lti_13_handler_paths(app):
    """Test if all handlers are correctly set with the LTI13Authenticator."""
    auth = MockLTI13Authenticator()
    handlers = auth.get_handlers(app)
    handler_paths = [route[0] for route in handlers]
    assert "/lti13/config" in handler_paths
    assert "/lti13/oauth_login" in handler_paths
    assert "/lti13/oauth_callback" in handler_paths
