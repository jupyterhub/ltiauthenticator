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

> **TIP**: Most Learning Management Systems (LMS's) require launches with `TLS` enabled (`https`). Consider tunneling your local JupyterHub service to a publicly available `https` link, such as with [`ngrok`](https://ngrok.com) or [`localtunnel`](https://github.com/localtunnel/localtunnel).
