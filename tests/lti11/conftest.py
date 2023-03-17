import os
import secrets
import time
from typing import Dict, Optional, Tuple
from unittest.mock import Mock

import pytest
from oauthlib.oauth1.rfc5849 import Client, signature
from tornado.httputil import HTTPServerRequest
from tornado.web import Application, RequestHandler


@pytest.fixture
def req_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/HEAD/oauthenticator/tests/mocks.py
    """

    def _req_handler(
        handler: RequestHandler,
        uri: str = "https://hub.example.com",
        method: str = "POST",
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

    return _req_handler


@pytest.fixture
def get_launch_args():
    """Create an LTI 1.1 launch request."""

    def _get_launch_args(
        roles: str = "Instructor",
        ext_roles: str = "urn:lti:instrole:ims/lis/Instructor",
        lms_vendor: str = "canvas",
        oauth_consumer_key: str = "my_consumer_key",
        oauth_consumer_secret: str = "my_shared_secret",
        oauth_callback: Optional[str] = "about:blank",
    ) -> Tuple[str, Dict[str, str], Dict[str, str]]:
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = secrets.token_urlsafe(32)
        args = {
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
        if oauth_callback is not None:
            args["oauth_callback"] = oauth_callback
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

        client = Client(
            client_key=oauth_consumer_key, client_secret=oauth_consumer_secret
        )

        args["oauth_signature"] = signature.sign_hmac_sha1_with_client(
            base_string, client
        )
        return launch_url, headers, args

    return _get_launch_args


@pytest.fixture
def auth_args():
    """
    Return a valid request arguments make from LMS to our tool (when authentication steps were success)
    """
    args = {
        "oauth_callback": [b"about:blank"],
        "oauth_consumer_key": [b"my_consumer_key"],
        "oauth_signature_method": [b"HMAC-SHA1"],
        "oauth_timestamp": [b"1585947271"],
        "oauth_nonce": [b"01fy8HKIASKuD9gK9vWUcBj9fql1nOCWfOLPzeylsmg"],
        "oauth_signature": [b"abc123"],
        "oauth_version": [b"1.0"],
        "context_id": [b"888efe72d4bbbdf90619353bb8ab5965ccbe9b3f"],
        "context_label": [b"intro101"],
        "context_title": [b"intro101"],
        "course_lineitems": [b"my.platform.com/api/lti/courses/1/line_items"],
        "custom_canvas_assignment_title": [b"test-assignment"],
        "custom_canvas_course_id": [b"616"],
        "custom_canvas_enrollment_state": [b"active"],
        "custom_canvas_user_id": [b"1091"],
        "custom_canvas_user_login_id": [b"student1@example.com"],
        "ext_roles": [b"urn:lti:instrole:ims/lis/Instructor"],
        "launch_presentation_document_target": [b"iframe"],
        "launch_presentation_height": [b"1000"],
        "launch_presentation_locale": [b"en"],
        "launch_presentation_return_url": [
            b"https: //illumidesk.instructure.com/courses/161/external_content/success/external_tool_redirect"
        ],
        "launch_presentation_width": [b"1000"],
        "lis_outcome_service_url": [
            b"http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=MTIzNDU6OjpzZWNyZXQ="
        ],
        "lis_person_contact_email_primary": [b"student1@example.com"],
        "lis_person_name_family": [b"Bar"],
        "lis_person_name_full": [b"Foo Bar"],
        "lis_person_name_given": [b"Foo"],
        "lti_message_type": [b"basic-lti-launch-request"],
        "lis_result_sourcedid": [b"feb-123-456-2929::28883"],
        "lti_version": [b"LTI-1p0"],
        "resource_link_id": [b"888efe72d4bbbdf90619353bb8ab5965ccbe9b3f"],
        "resource_link_title": [b"Test-Assignment-Another-LMS"],
        "roles": [b"Instructor"],
        "tool_consumer_info_product_family_code": [b"canvas"],
        "tool_consumer_info_version": [b"cloud"],
        "tool_consumer_instance_contact_email": [b"notifications@mylms.com"],
        "tool_consumer_instance_guid": [
            b"srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:test-lms"
        ],
        "tool_consumer_instance_name": [b"myorg"],
        "user_id": [b"185d6c59731a553009ca9b59ca3a885100000"],
        "user_image": [b"https://lms.example.com/avatar-50.png"],
    }
    return args
