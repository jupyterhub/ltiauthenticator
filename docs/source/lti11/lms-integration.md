# LMS Integration

## Open edX

1. You need access to [Open edX Studio](https://studio.edx.org/) to set up Open edX with LTI 1.1. You might have to contact your Open edX administrator to get access.

1. [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course) for your course.

1. Pick a name for Open edX to call your JupyterHub server.
   Then, along with the _`client key`_ and _`client secret`_ you [generated](getting-started.md#create-consumer-and-key), create a `LTI Passport String` in the following format: `your-hub-name:client-key:client-secret`.
   The `your-hub-name` value can be anything, but you'll be using it throughout Open edX to refer to your JupyterHub instance, so make it something meaningful and unique.

1. Then [add the Passport String](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-passport-to-the-course-configuration) to Open edX.
   Remember to save your changes when done!

1. In a Unit where you want there to be a link to the hub, [add an LTI Component](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-component-to-a-course-unit).

   You should enter the following information into the appropriate component settings:

   - **LTI ID**: The value you entered for `your-hub-name` above.

   - **LTI URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub is accessible at `http://datahub.berkeley.edu`, **LTI URL** should be `http://datahub.berkeley.edu/hub/lti/launch`

   - **LTI Launch Target**: Should be set to **New Window**.

   - **Custom parameters**: The only currently supported custom parameter are `next` and `custom_next`, which can contain the relative URL that the user should be redirected to after authentication. For example, if you are using [`nbgitpuller`](https://github.com/data-8/nbgitpuller) and want the user to see [this file](https://github.com/binder-examples/requirements/blob/master/index.ipynb) after logging in, you could set the field **Custom parameters** to the following string:

   ```js
   [
     "next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb",
   ];
   ```

   > **Note**: If you have a `base_url` set in your JupyterHub configuration, that should be prefixed to your next parameter. ([Further explanation](#common-gotchas))

1. Done! You can click the Link to see what the user workflow would look like. You can repeat step 6 in all the units that should have a link to the Hub for the user.

## Canvas

The setup for Canvas is very similar to the process for Open edX.

### Install JupyterHub as an External Tool

[Add a new external app configuration in Canvas](https://community.canvaslms.com/docs/DOC-13135-415257103).
You can name it anything, but you'll be using it throughout the Canvas course to refer to your JupyterHub instance, so make it something meaningful and unique.
Note that the right to create applications might be limited by your institution.
The basic information required to create an application in Canvas' `Manual entry` mode is:

- **Name**: the external tool name, such as `JupyterHub`
- **Consumer Key**: the [created consumer key](getting-started.md#create-consumer-and-key)
- **Secret Key**: the [shared secret](getting-started.md#create-consumer-and-key)
- **Launch URL**: `https://www.example.com/hub/lti/launch`
- **Domain**: optional
- **Privacy**: anonymous, email only, name only, or public
- **Custom Fields**: optional

Canvas also provides the option to add the external tool by selecting either the `Paste XML` or `By URL` items from the `Course --> Settings --> Apps --> +App` section.
In these cases, use the `/lti11/config` endpoint from your JupyterHub instance to copy/paste the configuration XML or add the URL when defining your external tool configuration with the `Paste XML` or `By URL` options, respectively.

The application can be created at the account level or the course level. If the application is created at the account level, it means that the application is available to all courses under the same account.

**Privacy Setting**:

- If you run the course in public mode, ltiauthenticator will parse the student's canvas ID as the JupyterHub username.
- If you run the course in anonymous mode, ltiauthenticator will fall back to the LTI user ID, an anonymized version.
  - Currently, the only method for de-anonymizing the LTI user ID in Canvas is with [the "masquerade" permission](https://canvas.instructure.com/doc/api/file.masquerading.html), which grants the user full access to act as any user account.
  - Unless you are able to obtain masquerade permissions, it is recommended to run the course in public mode.

### Create a new assignment.

1. Navigate to `Assignments -> Add Assignment`
1. For `Submission Type`, select `External Tool`
1. Click on the `Find` button and search for the external tool by name that you added in the step above. Selecting the external tool will prepopulate the URL field with the correct launch URL.

```{important}
Using the `Find` button to search for your external tool is necessary to ensure the LTI consumer key and shared secret are referenced correctly.
Else, your launch request will be recognized as unauthorized and responded to with `401 Unauthorized`.
```

4. (Recommended) Check the `Launch in a new tab` checkbox.
1. Append any custom parameters you wish (see next step)

   > **Note**: If you are creating assignments via the Canvas API, you need to use [these undocumented external tool fields](https://github.com/instructure/canvas-lms/issues/1315) when creating the assignment.

1. **Custom Parameters**: With Canvas users have the option to set custom fields with the Launch Request URL. Unlike Open edX, there is no method to include these custom parameters in the LTI launch request's form data. However, you can append custom parameters to the launch URL as query strings using proper [character encoding](https://developer.mozilla.org/en-US/docs/Glossary/percent-encoding) to preserve the query strings as they are passed through JupyterHub. You can perform this encoding manually, [programmatically](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode), or via an online tool.

   Before:

   ```
   https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb
   ```

   After:

   ```
   https://example.com/hub/lti/launch?custom_next=/hub/user-redirect/git-pull%3Frepo%3Dhttps%3A%2F%2Fgithub.com%2Fbinder-examples%2Frequirements%26subPath%3Dindex.ipynb
   ```

   Note that the _entire_ query string should not need to be escaped, just the portion that will be invoked after JupyterHub processes the `user-redirect` command.

1. Done! You can click the link to see what the user workflow would look like.
   You can repeat step 7 in all the units that should have a link to the Hub for the user.

## Moodle

### General Requirements

The Moodle setup is very similar to both the Open edX and Canvas setups described above. In addition to completing the steps from the [Getting Started sections](getting-started.md) ensure that:

1. You have access to a user with the Moodle Administrator role, or have another Moodle Role that gives you Permissions to manage `Activity Modules`.

2. You need to have enabled the [External Tool](https://docs.moodle.org/37/en/External_tool) Activity Module in your Moodle environment.

3. If your Moodle environment is using https, you should also use https for your JupyterHub.

### Configuration Steps

1. Navigate to the course where you would like to add JupyterHub as an external tool
1. Turn on editing and add an instance of the `External Tool Activity Module` (https://docs.moodle.org/37/en/External_tool_settings)

   1. Activity Name: This will be the name that appears in the course for students to click on to initiate the connection to your hub.
   1. Click 'Show more...' to add additional configuration settings:

   - **Tool name**: the external tool name, such as `JupyterHub`.
   - **Tool URL**: Should be set to `your-hub-url/hub/lti/launch`. So if your hub is accessible at `https://datahub.berkeley.edu`, _Tool URL_ should be
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

1.  If you have a `base_url` set in your JupyterHub configuration, this needs to be reflected in your launch URL and custom parameters. For example, if your `jupyterhub_config.py` file contains:

```python
c.JupyterHub.base_url = '/jupyter'
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
