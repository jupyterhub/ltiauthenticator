# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

##############################################################################
# LTI 1.3 Authenticator configuration
##############################################################################
# Authenticate users via LTI 1.3
c.JupyterHub.authenticator_class = "ltiauthenticator.lti13.auth.LTI13Authenticator"

# User name claim containing a string which will be used by Jupyterhub as user name.
# Must be a unique identifyer of the user on the LTI Platform (LMS).
c.LTI13Authenticator.username_key = os.environ["LTI13_USERNAME_KEY"]

# The LTI 1.3 authorization url. The url of the platforms (LMS) endpoint for OAuth2
# authentication
c.LTI13Authenticator.authorize_url = os.environ["LTI13_AUTHORIZE_URL"]

# The external tool's client id as represented within the platform (LMS)
# Note: the client id is not required by some LMS's for authentication.
# Only required, if the JupyterHub is suppose to send back information to the LMS
c.LTI13Authenticator.client_id = os.environ.get("LTI13_CLIENT_ID", "")

# The JWKS endpoint of the platform (LMS).
# Currently not used since JWK verification is off (hard coded).
c.LTI13Authenticator.endpoint = os.environ["LTI13_ENDPOINT"]

# The LTI 1.3 token url used to validate JWT signatures
c.LTI13Authenticator.token_url = os.environ["LTI13_TOKEN_URL"]
##############################################################################


# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get("DOCKER_SPAWN_CMD", "start-singleuser.sh")
c.DockerSpawner.cmd = spawn_cmd

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR") or "/home/jovyan/work"
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# Allowed admins
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.Authenticator.admin_users = [admin]
