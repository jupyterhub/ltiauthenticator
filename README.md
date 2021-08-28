# LTI Launch JupyterHub Authenticator

[![Documentation build status](https://img.shields.io/readthedocs/ltiauthenticator?logo=read-the-docs)](https://ltiauthenticator.readthedocs.io/en/latest/?badge=latest)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jupyterhub/ltiauthenticator/Tests?logo=github)](https://github.com/jupyterhub/ltiauthenticator/actions)
[![Latest PyPI version](https://img.shields.io/pypi/v/jupyterhub-ltiauthenticator?logo=pypi)](https://pypi.python.org/pypi/jupyterhub-ltiauthenticator)

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

### EdX

1.  You need access to [EdX Studio](https://studio.edx.org/) to set up LTI. You
    might have to contact your EdX Liaison to get access.

2.  [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course)
    for your course.

3.  Create a _client key_ and _client secret_ for use by edX to authenticate your hub. Open up any command line:

    1.  Run `openssl rand -hex 32` and save the output. This will be your LTI Client **Key**.
    2.  Run `openssl rand -hex 32` and save the output. This will be your LTI Client **Secret**.

    Now we will use these strings to allow edX and JupyterHub to authenticate each other.

    _Note_: These commands will simply generate strings for you, it will not store them anywhere on the computer. Therefore you do not need to run these commands on your JupyterHub server--we will be supplying them manually in the next few steps.

    _Note_: Anyone with these two strings will be able to access your hub, so keep them secure!!

4.  By default, the user's name will be the `custom_canvas_user_id` passed in by canvas. If you
    would like to use some other bit of information from the LTI request, you can pick what should
    be used as the user id.

    ```python
    # Set the user's email as their user id
    c.LTIAuthenticator.username_key = 'lis_person_contact_email_primary'
    ```

    A [partial list of keys in an LTI request](https://www.edu-apps.org/code.html#params)
    is available to help. Your LMS provider might also implement custom keys
    you can use.

5.  Pick a name for edX to call your JupyterHub server. Then, along with the two random strings you generated in step 4, paste them together to create an _LTI Passport String_ in the following format:

    ```
    your-hub-name:client-key:client-secret
    ```

    `your-hub-name` can be anything, but you'll be using it throughout edX to refer to your hub, so make it something meaningful and unique.

    Here's an example:

    ```
    stat100-jupyterhub:fca69fa2deda7d45dfdfa85f288d59b4b5f3d22bfca2ba891187fe5c551705a5:8ce3caca82f467f0896b92d548dfbddaca86edfcaaba8c9d6777dfae4d2e1db9
    ```

    Then [add the Passport String](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-passport-to-the-course-configuration)
    to EdX. Remember to save your changes when done!

6.  Configure JupyterHub to accept LTI Launch requests from EdX. You do this by
    supplying JupyterHub with the client key & secret generated in step 3 (you don't need the hub name from step 4).

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

7.  In a Unit where you want there to be a link to the hub,
    [add an LTI Component](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-component-to-a-course-unit).

    You should enter the following information into the appropriate component
    settings:

    **LTI ID**: The value you entered for `your-hub-name` in step 4.

    **LTI URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub
    is accessible at `http://datahub.berkeley.edu`, **LTI URL** should be
    `http://datahub.berkeley.edu/hub/lti/launch`

    **LTI Launch Target**: Should be set to **New Window**.

    **Custom parameters**: The only currently supported custom parameter is
    `next`, which can contain the relative URL that the user should be redirected
    to after authentication. For example, if you are using
    [nbgitpuller](https://github.com/data-8/nbgitpuller) and want the user to see
    [this file](https://github.com/binder-examples/requirements/blob/HEAD/index.ipynb) after
    logging in, you could set the **Custom parameters** field to the following
    string:

    ```js
    [
      "next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb",
    ];
    ```

    _Note_: If you have a `base_url` set in your jupyterhub configuration, that should be prefixed to your next parameter. ([Further explanation](#common-gotchas))

8.  You are done! You can click the Link to see what the user workflow would look
    like. You can repeat step 6 in all the units that should have a link to the
    Hub for the user.

## Canvas

The setup for Canvas is very similar to the process for edX.

_Note_: You will see **Client Key** and **Consumer Key** used interchangably.

_Note_: You will see **Client Secret** and **Secret Key** used interchangably.

1.  Create a _client key_ and _client secret_ for use by Canvas to authenticate your hub. Open up any command line:

    1.  Run `openssl rand -hex 32` and save the output. This will be your LTI Client **Key**.
    2.  Run `openssl rand -hex 32` and save the output. This will be your LTI Client **Secret**.

    Now we will use these strings to allow Canvas and JupyterHub to authenticate each other.

    _Note_: These commands will simply generate strings for you, it will not store them anywhere on the computer. Therefore you do not need to run these commands on your JupyterHub server--we will be supplying them manually in the next few steps.

    _Note_: Anyone with these two strings will be able to access your hub, so keep them secure!!

2.  [Add a new external app configuration in Canvas](https://community.canvaslms.com/docs/DOC-13135-415257103).
    You can name it anything, but you'll be using it throughout Canvas to refer to your hub, so make it
    something meaningful and unique. Note that the right to create applications might be limited by your
    institution. The basic information required to create an application in Canvas' "Manual entry" mode is:

    - **Name**
    - **Consumer Key** - from step 1
    - **Secret Key** - from step 1
    - **Launch URL** - `https://www.example.com/hub/lti/launch`
    - **Domain** - optional
    - **Privacy** - anonymous, email only, name only, or public
    - **Custom Fields** - optional

    There are other configuration types, eg. "Paste XML" which offer more options.

    The application can be created at the account level or the course level. If the application is created at the account level, it means that the application is available to all courses under the same account.

    **Privacy Setting**:

    - If you run the course in public mode, ltiauthenticator will parse the student's canvas ID as the JupyterHub username.
    - If you run the course in anonymous mode, ltiauthenticator will fall back to the LTI user ID, an anonymized version.
      - Currently, the only method for de-anonymizing the LTI user ID in Canvas is with [the "masquerade" permission](https://canvas.instructure.com/doc/api/file.masquerading.html), which grants the user full access to act as any user account.
      - Unless you are able to obtain masquerade permissions, it is recommended to run the course in public mode.

3.  Configure JupyterHub to accept LTI Launch requests from Canvas. You do this by
    supplying JupyterHub with the client key & secret generated in step 1.

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
    2.  **IMPORTANT:** Click "Find" and search for the tool you added in step 2. Click that and it will prepopulate the URL field with the one you supplied when creating the application. Using the "find" button to search for your tool is necessary to ensure the LTI key and secret are sent with the launch request.
    3.  Check the "Launch in a new tab" checkbox.
    4.  Append any custom parameters you wish (see next step)

    Note: If you are creating assignments via the Canvas API, you need to use [these undocumented external tool fields](https://github.com/instructure/canvas-lms/issues/1315) when creating the assignment.

5.  **Custom Parameters**. Apart from any custom fields you have defined in step 2, you can add custom parameters to any assignment. Unlike EdX, there is no method to include these custom parameters in the lti launch request's form data. However, you can append custom parameters to the launch URL as query strings using proper [character encoding](https://developer.mozilla.org/en-US/docs/Glossary/percent-encoding) to preserve the query strings as they are passed through JupyterHub. You can perform this encoding manually, [programmatically](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode), or via an online tool.

    Before:

    ```
    https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb
    ```

    After:

    ```
    https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull%3Frepo%3Dhttps%3A%2F%2Fgithub.com%2Fbinder-examples%2Frequirements%26subPath%3Dindex.ipynb
    ```

    Note that the _entire_ query string should not need to be escaped, just the portion that will be invoked after JupyterHub processes the `user-redirect` command.

6.  You are done! You can click the link to see what the user workflow would look
    like. You can repeat step 7 in all the units that should have a link to the
    Hub for the user.

## Moodle

The Moodle setup is very similar to both the examples outlined above.

1.  You need to be a Moodle Administrator, or have another Moodle Role that
    gives you Permissions to manage Activity Modules.

2.  You need to have enabled the ['External
    Tool'](https://docs.moodle.org/37/en/External_tool) Activity Module in your
    Moodle environment

3.  Create an _client-key_ for use by Moodle against your hub. You can do so by
    running `openssl rand -hex 32` and saving the output.

4.  Create an _client-secret_ for use by Moodle against your hub. You can do so
    by running `openssl rand -hex 32` and saving the output.

5.  If you are running Jupyterhub locally, you need to Configure it to accept
    LTI Launch requests from Moodle. You do this by enabling the LTI
    Authenticator class and giving JupyterHub access to the client key & secret
    generated in steps 3 and 4.

    juptyerhub_config.py:

    ```python
    c.JupyterHub.authenticator_class = 'ltiauthenticator.LTIAuthenticator'

    c.LTIAuthenticator.consumers = {
        "client-key": "client-secret"
    }
    ```

6.  If you are running Jupyterhub within a Kubernetes Cluster, deployed using
    helm, you need to supply the client key & secret via the chart yaml
    configuration.

    config.yaml:

    ```yaml
    hub:
      config:
        LTIAuthenticator:
          consumers:
            client-key: client-secret
        JupyterHub:
          authenticator_class: ltiauthenticator.LTIAuthenticator
    ```

7.  If your Moodle environment is using https, you should also use https for your JupyterHub.

8.  Once you hub is up and running with the new LTI configuration, you can now configure Moodle.

9.  In the Moodle course you wish to add, turn on editing, and add an instance of the External Tool Activity Module (https://docs.moodle.org/37/en/External_tool_settings)

    Activtiy Name: This will be the name that appears in the course for students
    to click on to initiate the connection to your hub.

    Click 'Show more...'

    - Tool name:
    - Tool URL: Should be set to `your-hub-url/hub/lti/launch`. So if your hub
      is accessible at `https://datahub.berkeley.edu`, _Tool URL_ should be
      `https://datahub.berkeley.edu/hub/lti/launch`.
    - Consumer Key: _client key_
    - Shared secret: _client secret_
    - Custom parameters:
    - Default launch container: This setting will define how the hub is
      presented to the student, whether it's embedded within a Moodle, with or
      without blocks, replaces the current window, or is displayed in a new
      window.

10. Click 'Save and return to course' or 'Save and display', you will them either be returned to the course page, or have you hub displayed.

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
      "next=/jupyter/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb",
    ];
    ```

2.  [401 Unauthorized] - [Canvas] Make sure you added your JupyterHub link by first specifying the tool via the 'Find' button (Step 4.2). Otherwise your link will not be sending the appropriate key and secret and your launch request will be recognized as unauthorized.
