""" Example JupyterHub configuration file with LTI 1.1 settings. """
import os


# Set port and IP
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000

# Custom base url
c.JupyterHub.base_url = "/"

# Set log level
c.Application.log_level = "DEBUG"

# Add an admin user for testing the admin page
c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary
# auth_state to ths spawner
c.Authenticator.enable_auth_state = True

# Set the LTI 1.1 authenticator.
c.JupyterHub.authenticator_class = "ltiauthenticator.lti13.auth.LTI13Authenticator"

# Use an LTI 1.3 claim to set the username.
c.LTI13Authenticator.username_key = "given_name"

# Add the LTI 1.3 configuration options
c.LTI13Authenticator.authorize_url = (
    os.getenv("OAUTH2_AUTHORIZE_URL")
    or "https://canvas.instructure.com/api/lti/authorize_redirect"
)
c.LTI13Authenticator.client_id = os.getenv("OAUTH_CLIENT_ID") or ""
c.LTI13Authenticator.endpoint = (
    os.getenv("LTI13_ENDPOINT")
    or "https://canvas.instructure.com/api/lti/security/jwks"
)
c.LTI13Authenticator.oauth_callback_url = (
    os.getenv("OAUTH_CALLBACK_URL")
    or "https://56d2f8492794.ngrok.io/hub/oauth_callback"
)
c.LTI13Authenticator.token_url = (
    os.getenv("OAUTH2_TOKEN_URL") or "https://canvas.instructure.com/login/oauth2/token"
)
c.JupyterHub.extra_handlers = [
    (r"/lti13/config$", "ltiauthenticator.lti13.handlers.LTI13ConfigHandler"),
    (r"/lti13/jwks$", "ltiauthenticator.lti13.handlers.LTI13JWKSHandler"),
]
