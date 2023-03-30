# LTI Launch JupyterHub Authenticator

[![Documentation build status](https://img.shields.io/readthedocs/ltiauthenticator?logo=read-the-docs)](https://ltiauthenticator.readthedocs.io/en/latest/?badge=latest)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jupyterhub/ltiauthenticator/Tests?logo=github)](https://github.com/jupyterhub/ltiauthenticator/actions)
[![Latest PyPI version](https://img.shields.io/pypi/v/jupyterhub-ltiauthenticator?logo=pypi)](https://pypi.python.org/pypi/jupyterhub-ltiauthenticator)

Implements the [LTI v1.1](http://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) and the [LTI 1.3](http://www.imsglobal.org/spec/lti/v1p3/impl) authenticators for use with JupyterHub.

This converts JupyterHub into a LTI **Tool Provider**, which can be then easily used with various **Tool Consumers**, such as Canvas, Open EdX, Moodle, Blackboard, etc.

So far, `ltiauthenticator` has been tested with [Open edX](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html), [Canvas](https://canvas.instructure.com/doc/api/file.tools_intro.html), and [Moodle](https://docs.moodle.org/311/en/LTI_and_Moodle). Documentation contributions are highly welcome!

Note that with these `LTI` authenticators going directly to the hub url will no longer allow you to log in. You _must_ visit the hub through an appropriate LTI 1.1 compliant Tool Consumer or LTI 1.3 compliant Platform (such as Canvas, Moodle, Open edX, etc.) to be able to log in.

> **Note**: LTI 1.1 identifies the LMS as the `Tool Consumer` and LTI 1.3 identifies the LMS as the `Platform` for for all practical purposes these terms are equivalent.

## Installation

You can install the authenticator from PyPI:

```bash
pip install jupyterhub-ltiauthenticator
```

## Using LTIAuthenticator

### LTI 1.1

#### Common Configuration Settings

Due to the fact that LTI 1.1 is an open standard, Learning Management System (LMS) vendors that adhere to the LTI 1.1 standard utilize the same configuration settings when integrating with an external tool. Some of these settings are included in a configuration endpoint to facilitate the JupyterHub's as an external tool with your LMS.

Start by following the steps below to configure your JupyterHub setup with the basic settings. Then, navigate to your LMS vendor's section to complete the installation and configuration steps.

> **Note**: if your LMS is not listed feel free to send us a PR with instructions for this new LMS.

The table below describes the configuration options available with the LTI v1.1 authenticator:

| LTI Authenticator Configuration Setting | Required | Description                                                              | Default                            |
| --------------------------------------- | -------- | ------------------------------------------------------------------------ | ---------------------------------- |
| config_description                      | No       | The LTI 1.1 external tool description                                    | `JupyterHub LTI 1.1 external tool` |
| config_icon                             | No       | The http/s URL with the LTI 1.1 icon                                     | `nil`                              |
| config_title                            | No       | The LTI 1.1 external tool Title                                          | `JupyterHub`                       |
| consumers                               | Yes      | The key/value pair that represents the client key and shared secret      | `{}`                               |
| username_key                            | No       | The LTI 1.1 launch parameter that contains the JupyterHub username value | `canvas_custom_user_id`            |

> **Note**: Throughout this document the terms **Client Key** and **Consumer Key** are used interchangeably to represent the LTI 1.1 `key` and **Client Secret**, **Secret Key**, and **Shared Secret** are used interchangably to represent the LTI 1.1 `secret`.

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

> **Note**: These commands will simply generate strings for you, it will not store them anywhere on the computer. Therefore you _do not_ need to run these commands within the environment where you are launching the JupyterHub server.

> **Note**: Anyone with these two strings will be able to access your hub, so keep them secure!!

#### The Username Key Setting (LTI11Authenticator.username_key)

Regardless of the LMS vendor you are using (Canvas, Moodle, Open edX, etc.), the user's name will default to use the `custom_canvas_user_id`. (This is due to legacy behavior and will default to a more generic LTI 1.1 parameter in a future release). Change the `username_key` setting if you would like to use another value from the LTI 1.1 launch request.

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
      authenticator_class: ltiauthenticator.LTIAuthenticator # LTI 1.1
    LTIAuthenticator:
      consumers: { "client-key": "client-secret" }
      username_key: "lis_person_contact_email_primary"
      config_icon: "https://my.static.assets/img/icon.jpg"
```

> **Note**: in the helm chart example configuration above `hub.config.LTI11Authenticator.username_key: lis_person_contact_email_primary` is equivalent to the standard JupyterHub configuration using `jupyterhub_config.py` with `c.LTI11Authenticator.username_key = lis_person_contact_email_primary`.

#### Configuration of LTI 1.1 with the Learning Management System

##### Open edX

1. You need access to [Open edX Studio](https://studio.edx.org/) to set up Open edX with LTI 1.1. You might have to contact your Open edX administrator to get access.

1. [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course) for your course.

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

   > **Note**: If you have a `base_url` set in your jupyterhub configuration, that should be prefixed to your next parameter. ([Further explanation](#common-gotchas))

1. You are done! You can click the Link to see what the user workflow would look like. You can repeat step 6 in all the units that should have a link to the Hub for the user.

##### Canvas

The setup for Canvas is very similar to the process for Open edX.

###### Install JupyterHub as an External Tool

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

###### Create a new assignment.

1. Navigate to `Assignments -> Add Assignment`
1. For `Submission Type`, select `External Tool`
1. **IMPORTANT:** Click on the `Find` button and search for the external tool by name that you added in the step above. Selecting the external tool will prepopulate the URL field with the correct launch URL. Using the `Find` button to search for your external tool is necessary to ensure the LTI consumer key and shared secret are referenced correctly.
1. (Recommended) Check the `Launch in a new tab` checkbox.
1. Append any custom parameters you wish (see next step)

   > **Note**: If you are creating assignments via the Canvas API, you need to use [these undocumented external tool fields](https://github.com/instructure/canvas-lms/issues/1315) when creating the assignment.

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

#### Moodle

##### General Requirements

The Moodle setup is very similar to both the Open edX and Canvas setups described above. In addition to completing the steps from the [common configuration settings section](#common-configuration-settings) ensure that:

1. You have access to a user with the Moodle Administrator role, or have another Moodle Role that gives you Permissions to manage `Activity Modules`.

1. You need to have enabled the [External Tool](https://docs.moodle.org/37/en/External_tool) Activity Module in your Moodle environment.

1. If your Moodle environment is using https, you should also use https for your JupyterHub.

##### Configuration Steps

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

#### Common Gotchas

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

1.  [401 Unauthorized] - [Canvas] Make sure you added your JupyterHub link by first specifying the tool via the 'Find' button (Step 4.2). Otherwise your link will not be sending the appropriate key and secret and your launch request will be recognized as unauthorized.

### LTI 1.3

#### Common Configuration Settings

Like LTI 1.1, LTI 1.3 is an open standard.
Many Learning Management System (LMS) vendors support the LTI 1.3 standard and as such vendors are able to integrate with various LMS's as External Tools.

Start by following the steps below to configure your JupyterHub setup with the basic settings.
Then, navigate to your LMS vendor's section to complete the installation and configuration steps.

> **Note**: if your LMS is not listed feel free to send us a PR with instructions for this new LMS.

The table below describes the configuration options available with the LTI v1.1 authenticator:

| LTI Authenticator Configuration Setting | Required | Description                                                              | Default                            |
| --------------------------------------- | -------- | ------------------------------------------------------------------------ | ---------------------------------- |
| config_description                      | No       | The LTI 1.1 external tool description                                    | `JupyterHub LTI 1.1 external tool` |
| config_icon                             | No       | The http/s URL with the LTI 1.1 icon                                     | `nil`                              |
| config_title                            | No       | The LTI 1.1 external tool Title                                          | `JupyterHub`                       |
| consumers                               | Yes      | The key/value pair that represents the client key and shared secret      | `{}`                               |
| username_key                            | No       | The LTI 1.1 launch parameter that contains the JupyterHub username value | `canvas_custom_user_id`            |

#### The Username Key Setting (LTI13Authenticator.username_key)

The username is inferred from the ID token sent by the platform (LMS) during the login flow based on the setting of the `username_key` traitlet.
The default is `email`, but all other top-level claims of the ID token may be chosen.
The list of available values depends on the LMS vendor you are using and how your LMS is configured, but you take a look at [this example](http://www.imsglobal.org/spec/lti/v1p3/#examplelinkrequest) to get an idea of the available values.
If you are in doubt about the content of the ID token sent by the LMS, you may use [an external test tool](https://saltire.lti.app/tool) with your LMS to capture the ID token.

Your LMS may provide additional keys in the LTI 1.3 login initiation flow that you can use to set the username.
In most cases these are located in the `https://purl.imsglobal.org/spec/lti/claim/custom` claim.
In this case, `username_key` must be prefixed with "custom_".
For example, `username_key` value "custom_uname" will set the username to the value of the parameter `uname` within the `https://purl.imsglobal.org/spec/lti/claim/custom` claim.

If your platform's LTI 1.3 settings are defined with privacy enabled or if the given `username_key` is not found within the ID token, then by default the `sub` claim is used to set the username.

You may also have the option of using [variable substitutions](http://www.imsglobal.org/spec/lti/v1p3/#customproperty) to fetch values that aren't provided with your vendor's standard LTI 1.3 login initiation flow request.

The example below illustrates how to fetch the user's given name to set the JupyterHub username:

```python
# Set the user's email as their user id
c.LTI13Authenticator.username_key = "given_name"
```

#### LTI 1.3 Configuration JSON Settings

The LTI 1.3 configuration JSON settings are available at `/lti13/config` endpoint. Some LMS vendors accept URLs that render the configuration JSON to simplify the LTI 1.3 tool installation process.

You may customize these settings with the `tool_name` and `tool_description` configuration options.

#### Custom Configuration with JupyterHub's Helm Chart

If you are running **JupyterHub within a Kubernetes Cluster**, deployed using helm, you need to supply the LTI 1.3 (OIDC/OAuth2) endpoints. The example below also demonstrates how customize the `lti13.username_key` to set the user's give name:

```yaml
# Custom config for JupyterHub's helm chart
hub:
  config:
    # Additional documentation related to authentication and authorization available at
    # https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html
    JupyterHub:
      authenticator_class: ltiauthenticator.lti13.auth.LTI13Authenticator
    LTI13Authenticator:
      # Use an LTI 1.3 claim to set the username. You can use and LTI 1.3 claim that
      # identifies the user, such as email, last_name, etc.
      username_key: "given_name"
      # The issuer identifyer of the platform
      issuer: "https://canvas.instructure.com"
      # The LTI 1.3 authorization url
      authorize_url: "https://canvas.instructure.com/api/lti/authorize_redirect"
      # The external tool's client id as represented within the platform (LMS)
      # Note: the client id is not required by some LMS's for authentication.
      client_id: "125900000000000329"
      # The LTI 1.3 endpoint url, also known as the OAuth2 callback url
      endpoint: "http://localhost:8000/hub/oauth_callback"
      # The LTI 1.3 token url used to validate JWT signatures
      token_url: "https://canvas.instructure.com/login/oauth2/token"
```

#### Configuration of LTI 1.3 with the Learning Management System

#### Canvas

The setup for the Canvas LMS.

##### Configure the JupyterHub as as a Developer Key

1. [To install the JupyterHub as an External Tool](https://community.canvaslms.com/t5/Canvas-Releases-Board/Canvas-Release-LTI-1-3-and-LTI-Advantage-2019-06-22/td-p/246652) admin users need to create a `Developer Key`. (More detailed instructions and screen shots on how to access this section are provided in the link above).

1. Once the Developer Key configuration for is open then select the `Enter URL` method within the `Configure` -> `Method` dropdown. This allows admin users to add the JupyterHub configuration by referring to a JupyterHub endpoint that renders the LTI 1.3 Developer Key configuration in JSON. By default the configuration URL is structured with the `https://<my-hub.domain.com>/hub/lti13/config` format.

1. Add the `Redirect URIs`. By default, the redirect URI is equivalent to the callback URL. As such the default URL for the Redirect URIs field should be `https://<my-hub.domain.com>/hub/oauth_callback`.

1. Add a `Key Name` to identify the `Developer Key`.

1. (Optional) Enter owner's email and developer key notes.

1. Save the `Developer Key` settings by clicking on the `Save` button.

##### Enable the Developer Key and copy Client ID

1. You should now see the new `Developer Key` in the `Admin` -> `Developer Keys` -> `Accounts` tab. By default the Developer Key is disabled. Enable the JupyterHub installation by clicking on the On/Off toggler in the `State` column to `ON`.

1. Copy the value that represents the `Client ID` in the `Datails` column. This value should look something like `125900000000000318`.

##### Install the JupyterHub as an External Tool in your Canvas Course

1. Navigate to the course where you would like to enable the JupyterHub.

1. Click on the course's `Settings` link.

1. Click on the `Apps` tab and then on `View App Configurations`.

1. Click on the `+App` button to add a new application. Select `By Client ID` from the `Configuration Type` dropdown and paste the `Client ID` value that you copied from the `Developer Keys` -> `<Your Developer Key Name>` -> `Details` column.

1. Save the application.

Once the application is saved you will see the option to launch the JupyterHub from the Course navigation menu. You will also have the option to add `Assignments` as an `External Tool`.

**Privacy Settings**:

Like the Privacy Settings for LTI 1.1, the LTI 1.3 External Tool application in [Canvas may be configured with privacy enabled](https://community.canvaslms.com/t5/Canvas-Developers-Group/LTI-1-3-Configuration-Claims-Course-Placement-Privacy/td-p/229252). The user ID in these cases will fetch the value from the LTI 1.3 subject (`sub` claim) which is a unique and opaque identifier for the student.

##### Create a new assignment as an External Tool

To configure an assignment with LTI 1.3 as an External Tool [follow the instructions from the LTI 1.1 -> Create a new assignment section](#create-a-new-assignment-as-an-external-tool).

#### Common Gotchas

Refer to the [common gotchas](#common-gotchas) section in the LTI 1.1 section.
