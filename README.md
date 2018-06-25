# LTI Launch JupyterHub Authenticator

[![Build Status](https://travis-ci.org/yuvipanda/jupyterhub-ltiauthenticator.svg?branch=master)](https://travis-ci.org/yuvipanda/jupyterhub-ltiauthenticator)

Implements [LTI v1](http://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) authenticator for use with JupyterHub.

This converts JupyterHub into a LTI **Tool Provider**, which can be
then easily used with various **Tool Consumers**, such as Canvas, EdX,
Moodle, Blackboard, etc.

So far, `ltiauthenticator` has been tested with [EdX](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html) and [Canvas](https://canvas.instructure.com/doc/api/file.tools_intro.html). Documentation contributions are highly welcome!

Note that with this authenticator, going directly to the hub url will no longer
allow you to log in. You _must_ visit the hub through an appropriate Tool
Consumer (such as EdX) to be able to log in.

## Installation

You can install the authenticator from PyPI:

```bash
pip install jupyterhub-ltiauthenticator
```

## Using LTIAuthenticator

_A note about LTI Passports: These can essentially be any 3 strings put together, but it is recommended to use the OpenSSL PRNG to create a pseudorandom 32 byte number._

### EdX

1.  You need access to [EdX Studio](https://studio.edx.org/) to set up LTI. You
    might have to contact your EdX Liaison to get access.

2.  [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course)
    for your course.

3.  [_Same as edX_] Create a _client key_ and _client secret_ for use by edX to authenticate your hub. You can do so by
    running `openssl rand -hex 32` twice and saving each output. These keys can actually be any two strings, but for security it is recommended to use strings with [high degrees of entropy](https://xkcd.com/936).

4.  Create an _LTI Passport String_ for use by EdX in the following format:

    ```
    your-hub-name:client-key:client-secret
    ```

    `your-hub-name` can be anything, but you'll need to use it later. So make it
    something memorable and unique.

    The [add the Passport String](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-passport-to-the-course-configuration)
    to EdX. Remember to save your changes when done!

5.  Configure JupyterHub to accept LTI Launch requests from EdX. You do this by
    giving JupyterHub access to the client key & secret generated in steps 3 and 4.

    ```python
    c.LTIAuthenticator.consumers = {
        "client-key": "client-secret"
    }
    ```

    A Hub can be configured to accept Launch requests from multiple Tool
    Consumers. You can do so by just adding all the client keys & secrets to the
    `c.LTIAuthenticator.consumers` traitlet like above.

6.  In a Unit where you want there to be a link to the hub,
    [add an LTI Component](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-component-to-a-course-unit).

    You should enter the following information into the appropriate component
    settings:

    **LTI ID**: The value you entered for `your-hub-name` in step 5.

    **LTI URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub
    is accessible at `http://datahub.berkeley.edu`, **LTI URL** should be
    `http://datahub.berkeley.edu/hub/lti/launch`

    **LTI Launch Target**: Should be set to **New Window**.

    **Custom parameters**: The only currently supported custom parameter is
    `next`, which can contain the relative URL that the user should be redirected
    to after authentication. For example, if you are using
    [nbgitpuller](https://github.com/data-8/nbgitpuller) and want the user to see
    [this file](https://github.com/binder-examples/requirements/blob/master/index.ipynb) after
    logging in, you could set the **Custom parameters** field to the following
    string:

    ```js
    [
      'next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb'
    ];
    ```

    Note here again that if you have a `base_url` set in your jupyterhub configuration, that should be prefixed to your next parameter.

7.  You are done! You can click the Link to see what the user workflow would look
    like. You can repeat step 7 in all the units that should have a link to the
    Hub for the user.

## Canvas

The setup for Canvas is very similar to the process for edX.

1.  [_Same as edX_] Create a _client key_ and _client secret_ for use by Canvas to authenticate your hub. You can do so by
    running `openssl rand -hex 32` twice and saving each output. These keys can actually be any two strings, but for security it is recommended to use strings with [high degrees of entropy](https://xkcd.com/936).

2.  Create an application called "Jupyter" in Canvas. Note that the right to create applications might be limited by your
    institution. The basic information required to create an application in Canvas' "Manual entry" mode is:

    - **Name**
    - **Consumer Key** - from step 1
    - **Secret Key** - from step 2
    - **Launch URL** - `https://www.example.com/hub/lti/launch`
    - **Domain** - optional
    - **Privacy** - anonymous, email only, name only, or public
    - **Custom Fields** - optional-

    There are other configuration types, eg. "Paste XML" which has more controls

    The application can be created at the account level or the course level. If the application is created at the account level, it means that the application is available to all courses under the same account.

3.  [Same as edX] Configure JupyterHub to accept LTI Launch requests from EdX. You do this by
    giving JupyterHub access to the client key & secret generated in steps 3 and 4.

    _Note: While you could paste these keys directly into your configuration file, they are secure credentials and should not be committed to any version control repositories. It is therefore best practice to store them securely. Here, we have stored them in environment variables._

    ```python
    c.JupyterHub.authenticator_class = 'ltiauthenticator.LTIAuthenticator'
    c.LTIAuthenticator.consumers = {
        os.environ['LTI_CLIENT_KEY']: os.environ['LTI_CLIENT_SECRET']
    }
    ```

    A Hub can be configured to accept Launch requests from multiple Tool
    Consumers. You can do so by just adding all the client keys & secrets to the
    `c.LTIAuthenticator.consumers` traitlet like above.

4.  Create a new assignment.

    1.  Make the submission type an external tool
    2.  **IMPORTANT:** Click "Find" and search for the tool you added in step 4. Click that, and it will prepopulate the URL you supplied. Using the "find" button to search for your tool is necessary to ensure the LTI key and secret are sent with the launch request.
    3.  Check the "Launch in a new window" checkbox.
    4.  Append any custom parameters you wish (see next step)

5.  **Custom Parameters**. Apart from any custom fields you have defined in step 1, you can add custom parameters to any assignment. Unlike EdX, there is no method to include these custom parameters in the lti launch request form data. However, you can append custom parameters to the launch URL as query strings--using proper [character encoding](https://developer.mozilla.org/en-US/docs/Glossary/percent-encoding) to preserve the query strings as they are passed through JupyterHub. You can perform this encoding manually, or you can use an online tool [such as this one](https://meyerweb.com/eric/tools/dencoder/).

    Before:

    ```
    https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb
    ```

    After:

    ```
    https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull%3Frepo%3Dhttps%3A%2F%2Fgithub.com%2Fbinder-examples%2Frequirements%26subPath%3Dindex.ipynb
    ```

    Note that the _entire_ query string should not need to be escaped, just the portion that will be invoked after JupyterHub processes the `user-redirect` command.

6.  [_Same as edX_] You are done! You can click the link to see what the user workflow would look
    like. You can repeat step 7 in all the units that should have a link to the
    Hub for the user.

## Debugging Note

JupyterHub preferentially uses any user_id cookie stored over an authentication request. Therefore, do not open multiple tabs at once and expect to be able to log in as separate users without logging out first! [Discussion](https://github.com/jupyterhub/jupyterhub/pull/1840)

## Common Gotchas

1.  If you have a base_url set in your jupyterhub configruation, this needs to be reflected in your launch URL and custom parameters. For example, if your `jupyterhub_config.py` file contains:

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
      'next=/jupyter/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb'
    ];
    ```
