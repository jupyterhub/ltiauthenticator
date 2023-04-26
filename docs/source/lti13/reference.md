# Configuration reference

This section describes the available configuration options for the various classes of the plugin.
Configuration is defined via `traitlets` of the classes and values are specified either in the [`jupyterhub_config.py`](https://jupyterhub.readthedocs.io/en/stable/getting-started/config-basics.html#configuration-basics) or by some other means depending on the JupyterHub deployment (e.g. the [JupyterHub helm chart](https://z2jh.jupyter.org/en/stable/administrator/authentication.html)).
For example, to set the `username_key` property of the `LTI13Authenticator` class, your `jupyterhub_config.py` file would contain the lines

```python
c.JupyterHub.authenticator_class = "ltiauthenticator.lti13.auth.LTI13Authenticator"
c.LTI13Authenticator.username_key = "email"
```

or your helm chart `config.yml` would contain

```yaml
hub:
  config:
    JupyterHub:
      authenticator_class: ltiauthenticator.lti13.auth.LTI13Authenticator
    LTI13Authenticator:
      username_key: "email"
```

## LTI13Authenticator

| Property         | Required | Description                                                                                                                                                                                                                   | Default                                                  |
| ---------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| tool_name        | No       | Name of the tool within the config JSON                                                                                                                                                                                       | `"JupyterHub"`                                           |
| tool_description | No       | Description of the tool within the config JSON                                                                                                                                                                                | `"Launch interactive Jupyter Notebooks with JupyterHub"` |
| username_key     | No       | The LTI 1.3 launch parameter that contains the JupyterHub username value                                                                                                                                                      | `"email"`                                                |
| issuer           | Yes      | The platform's issuer identifier. A case-sensitive URL provided by the platform                                                                                                                                               |                                                          |
| client_id        | Yes      | The client ID or a list of client IDs identifying the JuyterHub within the LMS platform. Must contain the client IDs created when registering the tool on the LMS platform. Possible values are of type `str` or `list[str]`. |                                                          |
| authorize_url    | Yes      | Authorization end-point of the platform's identity provider. Provided by the platform.                                                                                                                                        |                                                          |
| jwks_endpoint    | Yes      | Platform's jwks endpoint. Provided by the platform                                                                                                                                                                            |                                                          |
| jwks_algorithms  | No       | List of supported signature methods                                                                                                                                                                                           | `["RS256"]`                                              |

## LTI13LaunchValidator

| Setting     | Required | Description                                                                                    | Default |
| ----------- | -------- | ---------------------------------------------------------------------------------------------- | ------- |
| time_leeway | No       | A time margin in seconds to deal with time synchronization issues when checking JWT expiration | 0       |
| max_age     | No       | Maximum period in seconds in which an issued ID token is accepted                              | 600     |
