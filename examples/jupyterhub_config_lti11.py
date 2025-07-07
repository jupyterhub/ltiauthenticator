"""Example JupyterHub configuration file with LTI 1.1 settings."""

import os

# Set port and IP
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000

# Custom base url
c.JupyterHub.base_url = "/mytenant"

# Set log level
c.Application.log_level = "DEBUG"

# Add an admin user for testing the admin page
c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary
# auth_state to ths spawner
c.Authenticator.enable_auth_state = True

# Set the LTI 1.1 authenticator.
c.JupyterHub.authenticator_class = "ltiauthenticator.lti11.auth.LTI11Authenticator"

# Add the LTI 1.1 consumer key and shared secret. Note the use of
# `LTI11Authenticator` vs the legacy `LTIAuthenticator`.
c.LTI11Authenticator.consumers = {
    os.environ["LTI_CLIENT_KEY"]: os.environ["LTI_SHARED_SECRET"]
}

# Use an LTI 1.1 parameter to set the username.
c.LTI11Authenticator.username_key = "lis_person_name_full"
