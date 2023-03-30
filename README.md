# LTI JupyterHub Authenticator

[![Documentation build status](https://img.shields.io/readthedocs/ltiauthenticator?logo=read-the-docs)](https://ltiauthenticator.readthedocs.io/en/latest/?badge=latest)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jupyterhub/ltiauthenticator/Tests?logo=github)](https://github.com/jupyterhub/ltiauthenticator/actions)
[![Latest PyPI version](https://img.shields.io/pypi/v/jupyterhub-ltiauthenticator?logo=pypi)](https://pypi.python.org/pypi/jupyterhub-ltiauthenticator)

Implements the [LTI 1.3](http://www.imsglobal.org/spec/lti/v1p3/impl) and the [LTI v1.1](http://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide) authenticators for use with JupyterHub.

This converts JupyterHub into an LTI **Tool Provider**, which can be then easily be used with various **Tool Consumers**, such as Canvas, Open EdX, Moodle, Blackboard, etc.

So far, `ltiauthenticator` has been tested with [Open edX](http://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html), [Canvas](https://canvas.instructure.com/doc/api/file.tools_intro.html), and [Moodle](https://docs.moodle.org/311/en/LTI_and_Moodle). Documentation contributions are highly welcome!

Note that with these `LTI` authenticators going directly to the hub URL will no longer allow you to log in. You _must_ visit the hub through an appropriate LTI 1.1 compliant Tool Consumer or LTI 1.3 compliant Platform (such as Canvas, Moodle, Open edX, etc.) to be able to log in.

> **Note**: LTI 1.1 identifies the LMS as the `Tool Consumer` and LTI 1.3 identifies the LMS as the `Platform` for all practical purposes these terms are equivalent.

## Installation

You can install the authenticator from PyPI:

```bash
pip install jupyterhub-ltiauthenticator
```

## Using the LTI Authenticators

For detailed instructions on how to configure the `LTI13Authenticator` or `LTI11Authenticator` and integrate it with an LMS, such as Canvas, Open EdX, Moodle, Blackboard, etc., please take a look at the [documentation](https://ltiauthenticator.readthedocs.io/).
