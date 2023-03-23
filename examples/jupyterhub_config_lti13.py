""" Example JupyterHub configuration file with LTI 1.3 settings. """
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

# Define issuer identifier of the LMS platform
c.LTI13Authenticator.issuer = (
    os.getenv("LTI13_ISSUER") or "https://canvas.instructure.com"
)
# Add the LTI 1.3 configuration options
c.LTI13Authenticator.authorize_url = (
    os.getenv("LTI13_AUTHORIZE_URL")
    or "https://canvas.instructure.com/api/lti/authorize_redirect"
)
c.LTI13Authenticator.client_id = os.getenv("LTI13_OAUTH_CLIENT_ID") or ""
c.LTI13Authenticator.jwks_endpoint = (
    os.getenv("LTI13_JWKS_ENDPOINT")
    or "https://canvas.instructure.com/api/lti/security/jwks"
)
# Validator setting
c.LTI13LaunchValidator.time_leeway = int(os.getenv("LTI13_TIME_LEEWAY", "0"))
c.LTI13LaunchValidator.max_age = int(os.getenv("LTI13_MAX_AGE", "600"))
