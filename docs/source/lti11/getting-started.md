# Getting Started

## General Procedure

Due to the fact that LTI 1.1 is an open standard, Learning Management System (LMS) vendors that adhere to the LTI 1.1 standard utilize the same configuration settings when integrating with an external tool.
Some of these settings are included in a configuration endpoint to facilitate the JupyterHub's as an external tool with your LMS.

Start by following the steps below to configure your JupyterHub setup with the essential settings.
See the [configuration reference](reference) for a complete list of available configuration options.

After setting up the authenticator plugin navigate to the [integration section of your vendor's LMS](lms-integration) to complete the installation and configuration steps.

```{note}
If your LMS is not listed feel free to send us a PR with instructions for this new LMS.
```

```{note}
Throughout this document the terms **Client Key** and **Consumer Key** are used interchangeably to represent the LTI 1.1 `key` and **Client Secret**, **Secret Key**, and **Shared Secret** are used interchangeably to represent the LTI 1.1 `secret`.
```

## Create Consumer and Key

Create a _`client key`_ and _`client secret`_ for use by the LMS to authenticate your hub. Open a terminal and enter the `openssl` commands below to create these values:

```bash
# consumer key
openssl rand -hex 32
```

```bash
# shared secret
openssl rand -hex 32
```

```{caution}
Anyone with these two strings will be able to access your hub, so keep them secure!!
```

```{note}
These commands will simply generate strings for you, it will not store them anywhere on the computer. Therefore, you _do not_ need to run these commands within the environment where you are launching the JupyterHub server.
```

It's a good idea to exclude sensitive values from your code, including JupyterHub configuration files.
You can do that by storing both values from above in environmental variables

```bash
export LTI_CLIENT_KEY=<YOUR CLIENT KEY PRODUCED BY OPENSSL>
export LTI_SHARED_SECRET=<YOUR CLIENT SECRET PRODUCED BY OPENSSL>
```

and read them within the `jupyterhub_config.py` file like this

```python
import os
c.LTI11Authenticator.consumers = {
    os.environ["LTI_CLIENT_KEY"]: os.environ["LTI_SHARED_SECRET"]
}
```

The same pattern applies when using containers, for example by using the `ENV` directive with a Dockerfile or a `ConfigMap` when using Kubernetes.

## Set the Username Key

Regardless of the LMS vendor you are using (Canvas, Moodle, Open edX, etc.), the user's name will default to use the `custom_canvas_user_id`.
This is due to legacy behaviour and will default to a more generic LTI 1.1 parameter in a future release.
Change the `username_key` setting if you would like to use another value from the LTI 1.1 launch request.

The example below illustrates how to fetch the user's email to set the JupyterHub username by specifying the `lis_person_contact_email_primary` LTI 1.1 launch request parameter:

```python
# Set the user's email as their user id
c.LTIAuthenticator.username_key = 'lis_person_contact_email_primary'
```

A [partial list of keys in an LTI request](https://www.edu-apps.org/code.html#params) is available as a reference if you would like to use another value to set the JupyterHub username.
As a general rule of thumb, Personally Identifiable Information values are represented with the `lis_person_*` arguments in the launch request.

Your LMS provider might also implement custom keys you can use, such as with the use of [custom parameter substitution](https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide).
To find out which keys are sent by the LMS, you may register an [LTI test tool emulator](https://saltire.lti.app/tool) and inspect the payload of the LTI Launch request.

## Configuration XML Settings

The LTI 1.1 configuration XML settings are available at the `/lti11/config` endpoint. Some LMS vendors, such as [Canvas](lms-integration.md#canvas) accept XML and/or URLs that render the configuration XML to simplify the LTI 1.1 External Tool installation process.

You may customize these settings with the `config_*` configuration options described in the [configuration reference](reference.md#lti11authenticator) section.

## Custom Configuration with JupyterHub's Helm Chart

If you are running **JupyterHub within a Kubernetes Cluster**, deployed using helm, you need to supply the client key & shared secret with the `LTI11Authenticator.consumers` key. The example below also demonstrates how customize the `LTI11Authenticator.username_key` to set the user's email as the JupyterHub username and the `LTI11Authenticator.config_icon` to define a custom external tool icon when using the LTI 1.1 configuration XML endpoint:

```yaml
# Custom config for JupyterHub's helm chart
hub:
  config:
    # Additional documentation related to authentication and authorization available at
    # https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html
    JupyterHub:
      authenticator_class: ltiauthenticator.lti11.auth.LTI11Authenticator # LTI 1.1
    LTI11Authenticator:
      consumers: { "client-key": "client-secret" }
      username_key: "lis_person_contact_email_primary"
      config_icon: "https://my.static.assets/img/icon.jpg"
```

```{hint}
In the helm chart example configuration above `hub.config.LTI11Authenticator.username_key: "lis_person_contact_email_primary"` is equivalent to the standard JupyterHub configuration using `jupyterhub_config.py` with `c.LTI11Authenticator.username_key = "lis_person_contact_email_primary"`.
```
