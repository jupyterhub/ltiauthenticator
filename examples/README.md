# LTI Authenticator Examples

This folder contains various configuration examples that allows users to test different configuration settings with the LTI authenticators. The instructions for these examples are to configure your environment with `virtualenv`, however, custom configuration snippets are also provided (to the extent possible) to configure your environment with a `Kubernetes` based deployment.

To run these examples, you need to first setup your JupyterHub test environment with the LTI Authenticator and then update your configuration settings based on one of the examples described below.

## Prepare the test environment setup

### Install the JupyterHub with `virtualenv`

1. Create a virtual environment:

```bash
virtualenv -p python3 venv
source venv/bin/activate
```

2. Install [requirements](https://jupyterhub.readthedocs.io/en/stable/quickstart.html#installation):

```bash
python3 -m pip install jupyterhub
npm install -g configurable-http-proxy
python3 -m pip install notebook
```

3. Create your secure LTI 1.1 consumer key and shared secret values:

```bash
export LTI_CLIENT_KEY=$(openssl rand -hex 32)
export LTI_SHARED_SECRET=$(openssl rand -hex 32)
```

## Example 1: Testing the `username_key` settings with LTI 1.1 launches

This example demonstrates how users can change the `username_key` to fetch values from the LTI 1.1 launch request that can be used to set the username.

1. Confirm the `username_key` value in the provided `jupyterhub_config_lti11.py` example:

Edit the provided `jupyterhub_config_lti11.py` to change the `username_key` to another value to represent the
user's username. LTI 1.1 parameters that represent Personably Identifiable Information (PII) values have the `lis_person_*`
prefix. The included example has the `lis_person_name_full` LTI 1.1 parameter assigned to the `username_key`. A full list of the `lis_person_*` are available in the [IMS GLobal LTI 1.1 implementation guide](https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) -> Section 3 (Basic Launch Data).

You could also use a parameter substitution to extract PII values from your LMS. To obtain a full list of possible parameter substitution settings refer to the IMS Global LTI 1.1 [implementation guide](https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) -> Apendix C.2.

2. Start the JupyterHub with the example configuration for LTI 1.1:

```bash
jupyterhub --config /path/to/jupyterhub_config_lti11.py
```

3. Check the username by either viewing the [JupyterHub's username value in the control panel](https://jupyterhub.readthedocs.io/en/stable/reference/urls.html#hub-home) and/or view the JupyterHub logs to confirm what the username is set to.

If the actual username value is different from the expected username value, then view the JupyterHub logs in `debug` (the provided examples have `c.Application.log_level = "DEBUG"`) mode to confirm that the original launch request keys/values are correct.
