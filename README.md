# LTI Launch JupyterHub Authenticator

[![Documentation build status](https://img.shields.io/readthedocs/ltiauthenticator?logo=read-the-docs)](https://ltiauthenticator.readthedocs.io/en/latest/?badge=latest)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jupyterhub/ltiauthenticator/Tests?logo=github)](https://github.com/jupyterhub/ltiauthenticator/actions)
[![Latest PyPI version](https://img.shields.io/pypi/v/jupyterhub-ltiauthenticator?logo=pypi)](https://pypi.python.org/pypi/jupyterhub-ltiauthenticator)

Implements [LTI v1.1](http://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) authenticator for use with JupyterHub.

This converts JupyterHub into a LTI **Tool Provider**, which can be
then easily used with various **Tool Consumers**, such as Canvas, EdX,
Moodle, Blackboard, etc.

So far, `ltiauthenticator` has been tested with [EdX](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html), [Canvas](https://canvas.instructure.com/doc/api/file.tools_intro.html), and [Moodle](https://docs.moodle.org/311/en/LTI_and_Moodle). Documentation contributions are highly welcome!

Note that with this authenticator, going directly to the hub url will no longer allow you to log in. You _must_ visit the hub through an appropriate LTI 1.1 compliant Tool Consumer (such as Canvas, Moodle, EdX, etc) to be able to log in.

## Installation

You can install the authenticator from PyPI:

```bash
pip install jupyterhub-ltiauthenticator
```

## Using LTIAuthenticator

### Common Configuration Settings

Due to the fact that LTI 1.1 is an open standard Learning Management System (LMS) vendors that adhere to the LTI 1.1 standard utilize the same configuration settings when integrating with an external tool. Some of these settings are included in a configuration endpoint to facilitate the JupyterHub's as an external tool with your LMS.

Start by following the steps below to configure your JupyterHub setup with the basic settings. Then, navigate to your LMS vendor's section to complete the installation and configuration steps.

> **Note**: if you LMS is not listed feel free to send us a PR with instructions for this new LMS.

The table below describes the configuration options available with the LTI v1.1 authenticator:

| LTI Authenticator Configuration Setting | Required | Description                                                              | Default                            |
| --------------------------------------- | -------- | ------------------------------------------------------------------------ | ---------------------------------- |
| config_description                      | No       | The LTI 1.1 external tool description                                    | `JupyterHub LTI 1.1 external tool` |
| config_icon                             | No       | The http/s URL with the LTI 1.1 icon                                     | `nil`                              |
| config_title                            | No       | The LTI 1.1 external tool Title                                          | `JupyterHub`                       |
| consumers                               | Yes      | The key/value pair that represents the client key and shared secret      | `{}`                               |
| username_key                            | No       | The LTI 1.1 launch parameter that contains the JupyterHub username value | `canvas_custom_user_id`            |

> _Note_: Throughout this document the terms **Client Key** and **Consumer Key** are used interchangeably to represent the LTI 1.1 `key` and **Client Secret**, **Secret Key**, and **Shared Secret** are used interchangably to represent the LTI 1.1 `secret`.

#### The Consumers Setting (LTI11Authenticator.consumers)

Create a `_client key_` and `_client secret_` (also known as the `consumer key` and the `shared secret`) for use by the LMS to authenticate your hub. Open a terminal and enter the `openssl` commands below to create your LTI 1.1 to create these values:

```bash
# consumer key
openssl rand -hex 32
```

```bash
# shared secret
openssl rand -hex 32
```

It's a good idea to exclude sensitive values from your code, including JupyterHub configuration files. The `examples/jupyterhub_config_lti11.py` fetches the key/secret values created with the `openssl` command from environment variables and would therefore have to export the values to your shell session before starting the JupyterHub application:

```bash
export LTI_CLIENT_KEY=<output from openssl rand -hex 32 for the consumer key>
export LTI_SHARED_SECRET=<output from openssl rand -hex 32 for the shared secret>
```

The same pattern applies when using containers, for example by using the `ENV` directive with a Dockerfile or a `ConfigMap` when using Kubernetes.

> _Note_: These commands will simply generate strings for you, it will not store them anywhere on the computer. Therefore you _do not_ need to run these commands within the environment where you are launching the JupyterHub server.

> _Note_: Anyone with these two strings will be able to access your hub, so keep them secure!!

#### The Username Key Setting (LTI11Authenticator.username_key)

Regardless of the LMS vendor you are using (Canvas, Moodle, Open edX, etc), the user's name will default to use the `custom_canvas_user_id`. (This is due to legacy behavior and will default to a more generic LTI 1.1 parameter in a future release). Change the `username_key` setting if you would like to use another value from the LTI 1.1 launch request.

The example below illustrates how to fetch the user's email to set the JupyterHub username by specifying the `lis_person_contact_email_primary` LTI 1.1 launch request parameter:

```python
# Set the user's email as their user id
c.LTIAuthenticator.username_key = 'lis_person_contact_email_primary'
```

A [partial list of keys in an LTI request](https://www.edu-apps.org/code.html#params) is available as a reference if you would like to use another value to set the JupyterHub username. As a general rule of thumb, Personally Identifiable Information (PII) values are represented with the `lis_person_*` arguments in the launch request. Your LMS provider might also implement custom keys you can use, such as with the use of [custom parameter substitution](https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide).

#### LTI 1.1 Configuration XML Settings

The LTI 1.1 configuration XML settings are available at `/lti11/config` endpoint. Some LMS vendors accept XML and/or URLs that render the configuration XML to simplify the LTI 1.1 External Tool installation process.

You may customize these settings with the `config_*` configuration options described in the [common configuration settings](#common-configuration-settings) section.

#### Custom Configuration with JupyterHub's Helm Chart

If you are running **JupyterHub within a Kubernetes Cluster**, deployed using helm, you need to supply the client key & shared secret with the `lti.consumers` key. The example below also demonstrates how customize the `lti.username_key` to set the user's email as the JupyterHub username and the `lti.config_icon` to define a custom external tool icon when using the LTI 1.1 configuration XML endpoint:

```yaml
# Custom config for JupyterHub's helm chart
hub:
  config:
    # Additional documentation related to authentication and authorization available at
    # https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html
    JupyterHub:
      authenticator_class: lti
    LTI11Authenticator:
      consumers: { "client-key": "client-secret" }
      username_key: "lis_person_contact_email_primary"
      config_icon: "https://my.static.assets/img/icon.jpg"
```

_Note_: in the helm chart example configuration above `hub.config.LTI11Authenticator.username_key: lis_person_contact_email_primary` is equivalent to the standard JupyterHub configuration using `jupyterhub_config.py` with `c.LTI11Authenticator.username_key = lis_person_contact_email_primary`.

### Open edX

1. You need access to [Open edX Studio](https://studio.edx.org/) to set up Open edX with LTI 1.1. You might have to contact your Open edX administrator to get access.

1. [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course for your course.

1. Pick a name for Open edX to call your JupyterHub server. Then, along with the two random strings you generated in the [Common Settings -> Consumers](#consumers) section create an `LTI Passport String` in the following format:

   `your-hub-name:client-key:client-secret`

   The `your-hub-name` value can be anything, but you'll be using it throughout Open edX to refer to your JupyterHub instance, so make it something meaningful and unique.

1. Then [add the Passport String](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-passport-to-the-course-configuration) to Open edX. Remember to save your changes when done!

1. In a Unit where you want there to be a link to the hub, [add an LTI Component](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-component-to-a-course-unit).

   You should enter the following information into the appropriate component settings:

   - **LTI ID**: The value you entered for `your-hub-name` above.

   - **LTI URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub is accessible at `http://datahub.berkeley.edu`, **LTI URL** should be `http://datahub.berkeley.edu/hub/lti/launch`

   - **LTI Launch Target**: Should be set to **New Window**.

   - **Custom parameters**: The only currently supported custom parameter are `next` and `custom_next`, which can contain the relative URL that the user should be redirected to after authentication. For example, if you are using [nbgitpuller](https://github.com/data-8/nbgitpuller) and want the user to see [this file](https://github.com/binder-examples/requirements/blob/master/index.ipynb) after logging in, you could set the **Custom parameters** field to the following string:

   ```js
   [
     "next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb",
   ];
   ```

   _Note_: If you have a `base_url` set in your jupyterhub configuration, that should be prefixed to your next parameter. ([Further explanation](#common-gotchas))

1. You are done! You can click the Link to see what the user workflow would look like. You can repeat step 6 in all the units that should have a link to the Hub for the user.

## Canvas

The setup for Canvas is very similar to the process for Open edX.

### Install JupyterHub as an External Tool

[Add a new external app configuration in Canvas](https://community.canvaslms.com/docs/DOC-13135-415257103). You can name it anything, but you'll be using it throughout the Canvas course to refer to your JupyterHub instance, so make it something meaningful and unique. Note that the right to create applications might be limited by your institution. The basic information required to create an application in Canvas' `Manual entry` mode is:

- **Name**: the external tool name, such as `JupyterHub`
- **Consumer Key**: the consumer key from [common settings section](#common-configuration-settings)
- **Secret Key**: the shared secret from [common settings section](#common-configuration-settings)
- **Launch URL**: `https://www.example.com/hub/lti/launch`
- **Domain**: optional
- **Privacy**: anonymous, email only, name only, or public
- **Custom Fields**: optional

Canvas also provides the option to add the external tool by selecting either the `Paste XML` or `By URL` items from the `Course --> Settings --> Apps --> +App` section. In these cases, use the `/lti11/config` endpoint from your JupyterHub instance to copy/paste the configuration XML or add the URL when defining your external tool configuraiton with the `Paste XML` or `By URL` options, respectively.

The application can be created at the account level or the course level. If the application is created at the account level, it means that the application is available to all courses under the same account.

**Privacy Setting**:

- If you run the course in public mode, ltiauthenticator will parse the student's canvas ID as the JupyterHub username.
- If you run the course in anonymous mode, ltiauthenticator will fall back to the LTI user ID, an anonymized version.
  - Currently, the only method for de-anonymizing the LTI user ID in Canvas is with [the "masquerade" permission](https://canvas.instructure.com/doc/api/file.masquerading.html), which grants the user full access to act as any user account.
  - Unless you are able to obtain masquerade permissions, it is recommended to run the course in public mode.

#### Create a new assignment.

1. Navigate to `Assignments -> Add Assignment`
1. For `Submission Type`, select `External Tool`
1. **IMPORTANT:** Click on the `Find` button and search for the external tool by name that you added in the step above. Selecting the external tool will prepopulate the URL field with the correct launch URL. Using the `Find` button to search for your external tool is necessary to ensure the LTI consumer key and shared secret are referenced correctly.
1. (Recommended) Check the `Launch in a new tab` checkbox.
1. Append any custom parameters you wish (see next step)

   > _Note_: If you are creating assignments via the Canvas API, you need to use [these undocumented external tool fields](https://github.com/instructure/canvas-lms/issues/1315) when creating the assignment.

1. **Custom Parameters**: With Canvas users have the option to set custom fields with the Launch Request URL. Unlike Open edX, there is no method to include these custom parameters in the lti launch request's form data. However, you can append custom parameters to the launch URL as query strings using proper [character encoding](https://developer.mozilla.org/en-US/docs/Glossary/percent-encoding) to preserve the query strings as they are passed through JupyterHub. You can perform this encoding manually, [programmatically](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode), or via an online tool.

   Before:

   ```
   https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb
   ```

   After:

   ```
   https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull%3Frepo%3Dhttps%3A%2F%2Fgithub.com%2Fbinder-examples%2Frequirements%26subPath%3Dindex.ipynb
   ```

   Note that the _entire_ query string should not need to be escaped, just the portion that will be invoked after JupyterHub processes the `user-redirect` command.

1. You are done! You can click the link to see what the user workflow would look
   like. You can repeat step 7 in all the units that should have a link to the
   Hub for the user.

## Moodle

### General Requirements

The Moodle setup is very similar to both the Open edX and Canvas setups described above. In addition to completing the steps from the [common configuration settings section](#common-configuration-settings) ensure that:

1. You have access to a user with the Moodle Administrator role, or have another Moodle Role that gives you Permissions to manage `Activity Modules`.

1. You need to have enabled the [External Tool](https://docs.moodle.org/37/en/External_tool) Activity Module in your Moodle environment.

1. If your Moodle environment is using https, you should also use https for your JupyterHub.

### Configuration Steps

1. Navigate to the course where you would like to add JupyterHub as an external tool
1. Turn on editing and add an instance of the `External Tool Activity Module` (https://docs.moodle.org/37/en/External_tool_settings)

   1. Activtiy Name: This will be the name that appears in the course for students to click on to initiate the connection to your hub.
   1. Click 'Show more...' to add additional configuration settings:

   - **Tool name**: the external tool name, such as `JupyterHub`.
   - **Tool URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub
     is accessible at `https://datahub.berkeley.edu`, _Tool URL_ should be
     `https://datahub.berkeley.edu/hub/lti/launch`.
   - **Consumer Key**: _client key_
   - **Shared secret**: _client secret_
   - **Custom parameters**: this is an optional field that you could use to fetch additional values from the launch request.
   - **Default launch container**: This setting will define how the hub is
     presented to the end user, whether it's embedded within a Moodle, with or
     without blocks, replaces the current window, or is displayed in a new
     window.

1. Click `Save and return to course` or `Save and display`, you will either be returned to the course page or create an LTI 1.1 launch request to log into the JupyterHub instance.

## Common Gotchas

1.  If you have a `base_url` set in your jupyterhub configruation, this needs to be reflected in your launch URL and custom parameters. For example, if your `jupyterhub_config.py` file contains:

    ```python
    `c.JupyterHub.base_url = '/jupyter'`
    ```

    then your Launch URL would be:

    ```
    https://www.example.com/jupyter/hub/lti/launch
    ```

    A custom next parameter might look like:

    ```js
    [
      "next=/jupyter/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb",
    ];
    ```

2.  [401 Unauthorized] - [Canvas] Make sure you added your JupyterHub link by first specifying the tool via the 'Find' button (Step 4.2). Otherwise your link will not be sending the appropriate key and secret and your launch request will be recognized as unauthorized.
