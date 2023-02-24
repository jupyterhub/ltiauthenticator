# Development Deployment for LTI 1.3

This is a docker compose development deployment for Jupyterhub with ltiauthenticator using LTI 1.3.
It allows to test the [ltiauthenticator](https://github.com/jupyterhub/ltiauthenticator) package against the [LTI 1.3 DevKit](https://github.com/oat-sa/devkit-lti1p3) which is distributed separately.
This document provides information on how to set up and run both the dev deployment and the DevKit for local testing purposes.

## LTI 1.3 DevKit deployment

### Build and run

Clone the repository from Github to some location outside your project folder

```sh
git clone --depth 1 --branch 2.5.2 https://github.com/oat-sa/devkit-lti1p3.git
```

Switch to the newly created folder and build and run the docker stack

```sh
docker compose up -d
```

Then, install the required PHP dependencies

```
docker run --rm --interactive --tty \
  --volume $PWD:/app \
  composer install
```

After installation, the development kit is available on http://devkit-lti1p3.localhost

### Link to Hub deployment

To link the Jupyterhub and LTI platform deployments, add the LTI config to the DevKit deployment

```sh
cp <PATH-TO-LTIAUTHENTICATOR-PROJECT>/dev/devkit-lti1p3.yaml <PATH-TO-LTI-DEVKIT-DEPLOYMENT>/config/packages/lti1p3.yaml
```

## ltiauthenticator dev deployment

You need `docker` and `docker-compose` available on your local development machine.

### Build and run

Clone this repository to your local machine, if not already done.

```sh
git clone https://github.com/jupyterhub/ltiauthenticator.git
```

Switch to the `dev` subfolder and build the docker stack

```sh
cd dev
docker-compose build
```

This will pull a Jupyterhub image and installs your local development version of the `ltiauthenticator` package into it.
Then run the Jupyterhub:

```sh
docker compose up -d
```

This will make your hub available at http://dev-jh-lti.localhost:8000/.
To update the dev deployment with the most recent code changes, run both commands again.

Note that `devkit-lti1p3` must be running since the JupyterHub service will joint its network.

### Configure LTI13Authenticator

The relevant configuration for the LTI 1.3 authenticator within Jupyterhub can be set via environment variables in the [`docker-compose.yml`](./docker-compose.yml).
Those variables are prefixed by `LTI13`.

After applying changes to the configuration, refresh the compose project.

```sh
docker compose up -d
```
