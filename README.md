# LTI Launch JupyterHub Authenticator

[![Build Status](https://travis-ci.org/yuvipanda/jupyterhub-ltiauthenticator.svg?branch=master)](https://travis-ci.org/yuvipanda/jupyterhub-ltiauthenticator)

Implements [LTI v1](http://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) authenticator for use with JupyterHub.

This converts JupyterHub into a LTI **Tool Provider**, which can be
then easily used with various **Tool Consumers**, such as Canvas, EdX,
Moodle, Blackboard, etc.

It's only been tested with [EdX](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html) so far,
but compatibility with other Tool Consumers is expected to already work.
Documentation contributions are highly welcome!

Note that with this authenticator, going directly to the hub url will no longer
allow you to log in. You *must* visit the hub through an appropriate Tool
Consumer (such as EdX) to be able to log in.

## Installation

You can install the authenticator from PyPI:

```bash
pip install jupyterhub-ltiauthenticator
```

## Using LTIAuthenticator

### EdX

1. You need access to [EdX Studio](https://studio.edx.org/) to set up LTI. You
   might have to contact your EdX Liaison to get access.

2. [Enable LTI Components](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#enabling-lti-components-for-a-course) 
   for your course.

3. Create an *client key* for use by EdX against your hub. You can do so by
   running `openssl rand -hex 32` and saving the output.

4. Create an *client secret* for use by EdX against your hub. You can do so by
   running `openssl rand -hex 32` and saving the output.

5. Create an *LTI Passport String* for use by EdX in the following format:

   ```
   your-hub-name:client-key:client-secret
   ```
   
   `your-hub-name` can be anything, but you'll need to use it later. So make it
   something memorable and unique.
   
   The [add the Passport String](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html#adding-an-lti-passport-to-the-course-configuration)
   to EdX. Remember to save your changes when done!
   
6. Configure JupyterHub to accept LTI Launch requests from EdX. You do this by
   giving JupyterHub access to the client key & secret generated in steps 3 and 4.

   ```python
   c.LTIAuthenticator.consumers = {
       "client-key": "client-secret"
   }
   ```
   
   A Hub can be configured to accept Launch requests from multiple Tool
   Consumers. You can do so by just adding all the client keys & secrets to the
   `c.LTIAuthenticator.consumers` traitlet like above.
   
7. In a Unit where you want there to be a link to the hub,
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
   ["next=/user-redirect/git-pull?repo=https://github.com/binder-examples/requirements&subPath=index.ipynb"]
   ```

8. You are done! You can click the Link to see what the user workflow would look
   like. You can repeat step 7 in all the units that should have a link to the
   Hub for the user.
