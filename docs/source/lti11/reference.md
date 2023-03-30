# Configuration reference

This section describes the available configuration options for the various classes of the plugin.
Configuration is defined via `traitlets` of the classes and values are specified either in the [`jupyterhub_config.py`](https://jupyterhub.readthedocs.io/en/stable/getting-started/config-basics.html#configuration-basics) or by some other means depending on the JupyterHub deployment (e.g. the [JupyterHub helm chart](https://z2jh.jupyter.org/en/stable/administrator/authentication.html)).
For example, to set the `config_title` property of the `LTI11Authenticator` class, your `jupyterhub_config.py` file would contain the lines

```python
c.JupyterHub.authenticator_class = "ltiauthenticator.lti11.auth.LTI11Authenticator"
c.LTI11Authenticator.config_title = "Some Title"
```

or your helm chart `config.yml` would contain

```yaml
hub:
  config:
    JupyterHub:
      authenticator_class: ltiauthenticator.lti11.auth.LTI13Authenticator
    LTI11Authenticator:
      config_title: "Some Title"
```

## LTI11Authenticator

| Property           | Required | Description                                                              | Default                            |
| ------------------ | -------- | ------------------------------------------------------------------------ | ---------------------------------- |
| config_description | No       | The LTI 1.1 external tool description                                    | `JupyterHub LTI 1.1 external tool` |
| config_icon        | No       | The http/s URL with the LTI 1.1 icon                                     | `nil`                              |
| config_title       | No       | The LTI 1.1 external tool Title                                          | `JupyterHub`                       |
| consumers          | Yes      | The key/value pair that represents the client key and shared secret      | `{}`                               |
| username_key       | No       | The LTI 1.1 launch parameter that contains the JupyterHub username value | `canvas_custom_user_id`            |
