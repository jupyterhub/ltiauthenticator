import os
import secrets
import time

from oauthlib.oauth1.rfc5849 import signature

import pytest

from typing import Dict

from tornado.web import Application
from tornadoweb.web import RequestHandler
from tornado.httputil import HTTPServerRequest

from unittest.mock import Mock


@pytest.fixture(scope="function")
def make_lti11_basic_launch_request_args() -> Dict[str, str]:
    def _make_lti11_basic_launch_args(
        roles: str = "Instructor",
        ext_roles: str = "urn:lti:instrole:ims/lis/Instructor",
        lms_vendor: str = "canvas",
        oauth_consumer_key: str = "my_consumer_key",
        oauth_consumer_secret: str = "my_shared_secret",
    ):
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = secrets.token_urlsafe(32)
        args = {
            "oauth_callback": "about:blank",
            "oauth_consumer_key": oauth_consumer_key,
            "oauth_timestamp": str(int(oauth_timestamp)),
            "oauth_nonce": str(oauth_nonce),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_version": "1.0",
            "context_id": "888efe72d4bbbdf90619353bb8ab5965ccbe9b3f",
            "context_label": "Introduction to Data Science",
            "context_title": "Introduction101",
            "course_lineitems": "https://canvas.instructure.com/api/lti/courses/1/line_items",
            "custom_canvas_assignment_title": "test-assignment",
            "custom_canvas_course_id": "616",
            "custom_canvas_enrollment_state": "active",
            "custom_canvas_user_id": "1091",
            "custom_canvas_user_login_id": "student1@example.com",
            "ext_roles": ext_roles,
            "launch_presentation_document_target": "iframe",
            "launch_presentation_height": "1000",
            "launch_presentation_locale": "en",
            "launch_presentation_return_url": "https://canvas.instructure.com/courses/161/external_content/success/external_tool_redirect",
            "launch_presentation_width": "1000",
            "lis_outcome_service_url": "http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ=",
            "lis_person_contact_email_primary": "student1@example.com",
            "lis_person_name_family": "Bar",
            "lis_person_name_full": "Foo Bar",
            "lis_person_name_given": "Foo",
            "lti_message_type": "basic-lti-launch-request",
            "lis_result_sourcedid": "feb-123-456-2929::28883",
            "lti_version": "LTI-1p0",
            "resource_link_id": "888efe72d4bbbdf90619353bb8ab5965ccbe9b3f",
            "resource_link_title": "Test-Assignment",
            "roles": roles,
            "tool_consumer_info_product_family_code": lms_vendor,
            "tool_consumer_info_version": "cloud",
            "tool_consumer_instance_contact_email": "notifications@mylms.com",
            "tool_consumer_instance_guid": "srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms",
            "tool_consumer_instance_name": "myedutool",
            "user_id": "185d6c59731a553009ca9b59ca3a885100000",
            "user_image": "https://lms.example.com/avatar-50.png",
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
def make_lti11_encoded_args(make_lti11_basic_launch_request_args):
    """Create LTI 1.1 launch request with encoded args."""
    local_args = make_lti11_basic_launch_request_args()
    args = {}
    for k, values in local_args.items():
        args[k] = values[0].decode()
    return args


@pytest.fixture(scope="function")
def make_lti11_success_authentication_request_args():
    def _make_lti11_success_authentication_request_args(
        roles: str = "Instructor",
        ext_roles: str = "urn:lti:instrole:ims/lis/Instructor",
        lms_vendor: str = "canvas",
        oauth_consumer_key: str = "my_consumer_key",
    ):
        """
        Return a valid request arguments make from LMS to our tool (when authentication steps were success)
        """
        args = {
            "oauth_callback": ["about:blank".encode()],
            "oauth_consumer_key": [oauth_consumer_key.encode()],
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
            "ext_roles": [ext_roles.encode()],
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
            "roles": [roles.encode()],
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
