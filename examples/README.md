# LTI Authenticator Examples

## LTI 1.1

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

3. Start the JupyterHub with example configuration for LTI 1.1:

```bash
jupyterhub --config examples/jupyterhub_config_lti11.py
```

4. Configure [JupyterHub as an external tool and launch it from your LMS](../README.md#using-ltiauthenticator)

> **TIP**: Most Learning Management Systems (LMS's) require launches with `TLS` enabled (`https`). To avoid having to setup TSL consider tunneling your local JupyterHub service to a publicly available `https` link, such as with [`ngrok`](https://ngrok.com) or [`localtunnel`](https://github.com/localtunnel/localtunnel).

5. (Optional) Update the `username_key`:

Edit the provided `jupyterhub_config_lti11.py` to change the `username_key` to another value to represent the
user's username. LTI 1.1 parameters that represent Personably Identifiable Information (PII) have the `lis_person_*` prefix.
You could also use a parameter substitution to extract PII values from your LMS.

To obtain a full list of possible parameter substitution settings refer to the IMS Global LTI 1.1 [implementation guide](https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) -> Apendix C.2.
