import json
import os
import secrets
import time
import uuid
from io import StringIO

from oauthlib.oauth1.rfc5849 import signature

import pytest

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPResponse
from tornado.httputil import HTTPHeaders
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.web import RequestHandler

from typing import Dict

from unittest.mock import Mock
from unittest.mock import patch


@pytest.fixture(scope="module")
def auth_state_dict():
    authenticator_auth_state = {
        "name": "student1",
        "auth_state": {
            "course_id": "intro101",
            "course_lineitems": "my.platform.com/api/lti/courses/1/line_items",
            "lms_user_id": "185d6c59731a553009ca9b59ca3a885100000",
            "user_role": "Learner",
        },
    }
    return authenticator_auth_state


@pytest.fixture(scope="module")
def app():
    class TestHandler(RequestHandler):
        def get(self):
            self.write("test")

        def post(self):
            self.write("test")

    application = Application(
        [
            (r"/", TestHandler),
        ]
    )  # noqa: E231
    return application


@pytest.fixture(scope="function")
def jupyterhub_api_environ(monkeypatch):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv("JUPYTERHUB_API_TOKEN", str(uuid.uuid4()))
    monkeypatch.setenv("JUPYTERHUB_API_URL", "https://localhost/hub/api")
    monkeypatch.setenv("JUPYTERHUB_ADMIN_USER", "admin")


@pytest.fixture(scope="function")
def lti11_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv("LTI_CONSUMER_KEY", "ild_test_consumer_key")
    monkeypatch.setenv("LTI_SHARED_SECRET", "ild_test_shared_secret")


@pytest.fixture(scope="function")
def lti11_complete_launch_args():
    """
    Valid response when retrieving jwks from the platform.
    """
    args = {
        "oauth_callback": ["about:blank".encode()],
        "oauth_consumer_key": ["my_consumer_key".encode()],
        "oauth_signature_method": ["HMAC-SHA1".encode()],
        "oauth_timestamp": ["1585947271".encode()],
        "oauth_nonce": ["01fy8HKIASKuD9gK9vWUcBj9fql1nOCWfOLPzeylsmg".encode()],
        "oauth_signature": ["abc123".encode()],
        "oauth_version": ["1.0".encode()],
        "context_id": ["888efe72d4bbbdf90619353bb8ab5965ccbe9b3f".encode()],
        "context_label": ["intro101".encode()],
        "context_title": ["intro101".encode()],
        "custom_canvas_assignment_title": ["test-assignment".encode()],
        "custom_canvas_user_login_id": ["student1".encode()],
        "custom_worskpace_type": ["foo".encode()],
        "ext_roles": ["urn:lti:instrole:ims/lis/Learner".encode()],
        "launch_presentation_document_target": ["iframe".encode()],
        "launch_presentation_height": ["1000".encode()],
        "launch_presentation_locale": ["en".encode()],
        "launch_presentation_return_url": [
            "https: //illumidesk.instructure.com/courses/161/external_content/success/external_tool_redirect".encode()
        ],
        "launch_presentation_width": ["1000".encode()],
        "lis_outcome_service_url": [
            "http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ=".encode()
        ],
        "lis_person_contact_email_primary": ["student1@example.com".encode()],
        "lis_person_name_family": ["Bar".encode()],
        "lis_person_name_full": ["Foo Bar".encode()],
        "lis_person_name_given": ["Foo".encode()],
        "lti_message_type": ["basic-lti-launch-request".encode()],
        "lis_result_sourcedid": ["feb-123-456-2929::28883".encode()],
        "lti_version": ["LTI-1p0".encode()],
        "resource_link_id": ["888efe72d4bbbdf90619353bb8ab5965ccbe9b3f".encode()],
        "resource_link_title": ["Test-Assignment-Another-LMS".encode()],
        "roles": ["Learner".encode()],
        "tool_consumer_info_product_family_code": ["canvas".encode()],
        "tool_consumer_info_version": ["cloud".encode()],
        "tool_consumer_instance_contact_email": ["notifications@mylms.com".encode()],
        "tool_consumer_instance_guid": [
            "srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms".encode()
        ],
        "tool_consumer_instance_name": ["myorg".encode()],
        "user_id": ["185d6c59731a553009ca9b59ca3a885100000".encode()],
        "user_image": ["https://lms.example.com/avatar-50.png".encode()],
    }
    return args


@pytest.fixture
def mock_jhub_user(request):
    """
    Creates an Authenticated User mock by returning a wrapper function to help us to customize its creation
    Usage:
        user_mocked = mock_jhub_user(environ={'USER_ROLE': 'Instructor'})
        or
        user_mocked = mock_jhub_user()
        or
        user_mocked = mock_jhub_user(environ={'USER_ROLE': 'Instructor'}, auth_state=[])
    """

    def _get_with_params(environ: dict = None, auth_state: list = []) -> Mock:
        """
        wrapper function that accept environment and auth_state
        Args:
            auth_state: Helps with the `the get_auth_state` method
        """
        mock_user = Mock()
        mock_spawner = Mock()
        # define the mock attrs
        spawner_attrs = {"environment": environ or {}}
        mock_spawner.configure_mock(**spawner_attrs)
        attrs = {
            "name": "user1",
            "spawner": mock_spawner,
            "get_auth_state.side_effect": auth_state or [],
        }
        mock_user.configure_mock(**attrs)
        return mock_user

    return _get_with_params


@pytest.fixture(scope="function")
def make_mock_request_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
    """

    def _make_mock_request_handler(
        handler: RequestHandler,
        uri: str = "https://hub.example.com",
        method: str = "GET",
        **settings: dict,
    ) -> RequestHandler:
        """Instantiate a Handler in a mock application"""
        application = Application(
            hub=Mock(
                base_url="/hub/",
                server=Mock(base_url="/hub/"),
            ),
            cookie_secret=os.urandom(32),
            db=Mock(rollback=Mock(return_value=None)),
            **settings,
        )
        request = HTTPServerRequest(
            method=method,
            uri=uri,
            connection=Mock(),
        )
        handler = RequestHandler(
            application=application,
            request=request,
        )
        handler._transforms = []
        return handler

    return _make_mock_request_handler


@pytest.fixture(scope="function")
def make_http_response() -> HTTPResponse:
    async def _make_http_response(
        handler: RequestHandler,
        code: int = 200,
        reason: str = "OK",
        headers: HTTPHeaders = HTTPHeaders({"content-type": "application/json"}),
        effective_url: str = "http://hub.example.com/",
        body: Dict[str, str] = {"foo": "bar"},
    ) -> HTTPResponse:
        """
        Creates an HTTPResponse object from a given request.

        Args:
          handler: tornado.web.RequestHandler object.
          code: response code, e.g. 200 or 404
          reason: reason phrase describing the status code
          headers: HTTPHeaders (response header object), use the dict within the constructor, e.g.
            {"content-type": "application/json"}
          effective_url: final location of the resource after following any redirects
          body: dictionary that represents the StringIO (buffer) body

        Returns:
          A tornado.client.HTTPResponse object
        """
        dict_to_buffer = StringIO(json.dumps(body)) if body is not None else None
        return HTTPResponse(
            request=handler,
            code=code,
            reason=reason,
            headers=headers,
            effective_url=effective_url,
            buffer=dict_to_buffer,
        )

    return _make_http_response


@pytest.fixture(scope="function")
def http_async_httpclient_with_simple_response(
    request, make_http_response, make_mock_request_handler
):
    """
    Creates a patch of AsyncHttpClient.fetch method, useful when other tests are making http request
    """
    local_handler = make_mock_request_handler(RequestHandler)
    test_request_body_param = (
        request.param if hasattr(request, "param") else {"message": "ok"}
    )
    with patch.object(
        AsyncHTTPClient,
        "fetch",
        return_value=make_http_response(
            handler=local_handler.request, body=test_request_body_param
        ),
    ):
        yield AsyncHTTPClient()


@pytest.fixture(scope="function")
def make_auth_state_dict() -> Dict[str, str]:
    """
    Creates an authentication dictionary with default name and auth_state k/v's
    """

    def _make_auth_state_dict(
        username: str = "foo",
        assignment_name: str = "myassignment",
        course_id: str = "intro101",
        lms_user_id: str = "abc123",
        user_role: str = "Learner",
    ):
        return {
            "name": username,
            "auth_state": {
                "assignment_name": assignment_name,
                "course_id": course_id,
                "lms_user_id": lms_user_id,
            },  # noqa: E231
        }

    return _make_auth_state_dict


@pytest.fixture(scope="function")
def make_lti11_basic_launch_request_args() -> Dict[str, str]:
    def _make_lti11_basic_launch_args(
        oauth_consumer_key: str = "my_consumer_key",
        oauth_consumer_secret: str = "my_shared_secret",
    ):
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = secrets.token_urlsafe(32)
        args = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0".encode(),
            "resource_link_id": "88391-e1919-bb3456",
            "oauth_consumer_key": oauth_consumer_key,
            "oauth_timestamp": str(int(oauth_timestamp)),
            "oauth_nonce": str(oauth_nonce),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_callback": "about:blank",
            "oauth_version": "1.0",
            "user_id": "123123123",
        }
        extra_args = {"my_key": "this_value"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        launch_url = "http://jupyterhub/hub/lti/launch"

        args.update(extra_args)

        base_string = signature.signature_base_string(
            "POST",
            signature.base_string_uri(launch_url),
            signature.normalize_parameters(
                signature.collect_parameters(body=args, headers=headers)
            ),
        )

        args["oauth_signature"] = signature.sign_hmac_sha1(
            base_string, oauth_consumer_secret, None
        )
        return args

    return _make_lti11_basic_launch_args


@pytest.fixture(scope="function")
def make_lti11_success_authentication_request_args():
    def _make_lti11_success_authentication_request_args(
        lms_vendor: str = "canvas", role: str = "Instructor"
    ) -> Dict[str, str]:
        """
        Return a valid request arguments make from LMS to our tool (when authentication steps were success)
        """
        args = {
            "oauth_callback": ["about:blank".encode()],
            "oauth_consumer_key": ["my_consumer_key".encode()],
            "oauth_signature_method": ["HMAC-SHA1".encode()],
            "oauth_timestamp": ["1585947271".encode()],
            "oauth_nonce": ["01fy8HKIASKuD9gK9vWUcBj9fql1nOCWfOLPzeylsmg".encode()],
            "oauth_signature": ["abc123".encode()],
            "oauth_version": ["1.0".encode()],
            "context_id": ["888efe72d4bbbdf90619353bb8ab5965ccbe9b3f".encode()],
            "context_label": ["intro101".encode()],
            "context_title": ["intro101".encode()],
            "course_lineitems": [
                "my.platform.com/api/lti/courses/1/line_items".encode()
            ],
            "custom_canvas_assignment_title": ["test-assignment".encode()],
            "custom_canvas_course_id": ["616".encode()],
            "custom_canvas_enrollment_state": ["active".encode()],
            "custom_canvas_user_id": ["1091".encode()],
            "custom_canvas_user_login_id": ["student1@example.com".encode()],
            "ext_roles": ["urn:lti:instrole:ims/lis/Learner".encode()],
            "launch_presentation_document_target": ["iframe".encode()],
            "launch_presentation_height": ["1000".encode()],
            "launch_presentation_locale": ["en".encode()],
            "launch_presentation_return_url": [
                "https: //illumidesk.instructure.com/courses/161/external_content/success/external_tool_redirect".encode()
            ],
            "launch_presentation_width": ["1000".encode()],
            "lis_outcome_service_url": [
                "http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ=".encode()
            ],
            "lis_person_contact_email_primary": ["student1@example.com".encode()],
            "lis_person_name_family": ["Bar".encode()],
            "lis_person_name_full": ["Foo Bar".encode()],
            "lis_person_name_given": ["Foo".encode()],
            "lti_message_type": ["basic-lti-launch-request".encode()],
            "lis_result_sourcedid": ["feb-123-456-2929::28883".encode()],
            "lti_version": ["LTI-1p0".encode()],
            "resource_link_id": ["888efe72d4bbbdf90619353bb8ab5965ccbe9b3f".encode()],
            "resource_link_title": ["Test-Assignment-Another-LMS".encode()],
            "roles": [role.encode()],
            "tool_consumer_info_product_family_code": [lms_vendor.encode()],
            "tool_consumer_info_version": ["cloud".encode()],
            "tool_consumer_instance_contact_email": [
                "notifications@mylms.com".encode()
            ],
            "tool_consumer_instance_guid": [
                "srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms".encode()
            ],
            "tool_consumer_instance_name": ["myorg".encode()],
            "user_id": ["185d6c59731a553009ca9b59ca3a885100000".encode()],
            "user_image": ["https://lms.example.com/avatar-50.png".encode()],
        }
        return args

    return _make_lti11_success_authentication_request_args


@pytest.fixture(scope="function")
def make_mock_request_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
    """

    def _make_mock_request_handler(
        handler: RequestHandler,
        uri: str = "https://hub.example.com",
        method: str = "GET",
        **settings: dict,
    ) -> RequestHandler:
        """Instantiate a Handler in a mock application"""
        application = Application(
            hub=Mock(
                base_url="/hub/",
                server=Mock(base_url="/hub/"),
            ),
            cookie_secret=os.urandom(32),
            db=Mock(rollback=Mock(return_value=None)),
            **settings,
        )
        request = HTTPServerRequest(
            method=method,
            uri=uri,
            connection=Mock(),
        )
        handler = RequestHandler(
            application=application,
            request=request,
        )
        handler._transforms = []
        return handler

    return _make_mock_request_handler
