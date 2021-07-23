import json
import os
import secrets
import time
from io import StringIO

from Crypto.PublicKey import RSA

import jwt

from oauthlib.oauth1.rfc5849 import signature

import pytest

from tornado.httpclient import HTTPResponse
from tornado.httputil import HTTPHeaders
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.web import RequestHandler

from typing import Dict
from typing import List

from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import HTTPServerRequest
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.web import RequestHandler

from unittest.mock import patch
from unittest.mock import Mock


@pytest.fixture(scope="function")
def user_model(username: str, **kwargs) -> dict:
    """Return a user model"""
    user = {
        "username": username,
        "auth_state": {k: v for k, v in kwargs.items() if not k.startswith("oauth_")},
    }
    user.update(kwargs)
    return user


@pytest.fixture(scope="function")
def make_http_response() -> HTTPResponse:
    """Creates an HTTPResponse

    Returns:
        HTTPResponse: [description]
    """

    def _make_http_response(
        handler: RequestHandler,
        code: int = 200,
        reason: str = "OK",
        headers: HTTPHeaders = HTTPHeaders({"content-type": "application/json"}),
        effective_url: str = "http://hub.example.com/",
        body: Dict[str, str] = {"foo": "bar"},
    ) -> HTTPResponse:
        """
        Creates an HTTPResponse object from a given request.

        Example:

            local_handler = make_mock_request_handler(RequestHandler)
            response_args = {'handler': local_handler.request, 'body': {'code': 200}}
            http_response = await factory_http_response(**response_args)

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
def make_lti11_success_authentication_request_args():
    def _make_lti11_success_authentication_request_args(
        role: str = "Instructor",
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
            "resource_link_title": ["JupyterHub".encode()],
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

    return _make_mock_request_handler


@pytest.fixture(scope="function")
def lti13_config_environ(monkeypatch, pem_file):
    """
    Set the enviroment variables used in Course class
    """
    monkeypatch.setenv("LTI13_PRIVATE_KEY", pem_file)
    monkeypatch.setenv(
        "LTI13_ENDPOINT", "https://my.platform.domain/api/lti/security/jwks"
    )
    monkeypatch.setenv(
        "OAUTH2_TOKEN_URL", "https://my.platform.domain/login/oauth2/token"
    )
    monkeypatch.setenv(
        "OAUTH2_CLIENT_ID", "https://my.platform.domain/login/oauth2/token"
    )
    monkeypatch.setenv(
        "OAUTH2_AUTHORIZE_URL", "https://my.platform.domain/api/lti/authorize_redirect"
    )


@pytest.fixture(scope="function")
def lti13_login_params():
    """
    Creates a dictionary with k/v's that emulates an initial login request.
    """
    client_id = "125900000000000085"
    iss = "https://platform.vendor.com"
    login_hint = "185d6c59731a553009ca9b59ca3a885104ecb4ad"
    target_link_uri = "https://edu.example.com/hub"
    lti_message_hint = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA"

    params = {
        "client_id": [client_id.encode()],
        "iss": [iss.encode()],
        "login_hint": [login_hint.encode()],
        "target_link_uri": [target_link_uri.encode()],
        "lti_message_hint": [lti_message_hint.encode()],
    }
    return params


@pytest.fixture(scope="function")
def lti13_login_params_decoded():
    """
    Creates a dictionary with k/v's that emulates an initial login request.
    """
    client_id = "125900000000000085"
    iss = "https://platform.vendor.com"
    login_hint = "185d6c59731a553009ca9b59ca3a885104ecb4ad"
    target_link_uri = "https://edu.example.com/hub"
    lti_message_hint = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA"

    params = {
        "client_id": [client_id],
        "iss": [iss],
        "login_hint": [login_hint],
        "target_link_uri": [target_link_uri],
        "lti_message_hint": [lti_message_hint],
    }
    return params


@pytest.fixture(scope="function")
def make_lti13_resource_link_request() -> Dict[str, str]:
    """
    Returns valid json after decoding JSON Web Token (JWT) for resource link launch (core).
    """
    jws = {
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
            "id": "b81accac78543cb7cd239f3792bcfdc7c6efeadb",
            "description": None,
            "title": None,
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "aud": "125900000000000071",
        "azp": "125900000000000071",
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "847:b81accac78543cb7cd239f3792bcfdc7c6efeadb",
        "exp": 1589843421,
        "iat": 1589839821,
        "iss": "https://canvas.instructure.com",
        "nonce": "125687018437687229621589839822",
        "sub": "8171934b-f5e2-4f4e-bdbd-6d798615b93e",
        "https://purl.imsglobal.org/spec/lti/claim/target_link_uri": "https://edu.example.com/hub",
        "https://purl.imsglobal.org/spec/lti/claim/context": {
            "id": "b81accac78543cb7cd239f3792bcfdc7c6efeadb",
            "label": "intro101",
            "title": "intro101",
            "type": ["http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering"],
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "https://purl.imsglobal.org/spec/lti/claim/tool_platform": {
            "guid": "srnuz6h1U8kOMmETzoqZTJiPWzbPXIYkAUnnAJ4u:canvas-lms",
            "name": "IllumiDesk",
            "version": "cloud",
            "product_family_code": "canvas",
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "https://purl.imsglobal.org/spec/lti/claim/launch_presentation": {
            "document_target": "iframe",
            "height": 400,
            "width": 800,
            "return_url": "https://illumidesk.instructure.com/courses/147/external_content/success/external_tool_redirect",
            "locale": "en",
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "locale": "en",
        "https://purl.imsglobal.org/spec/lti/claim/roles": [
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#User",
        ],
        "https://purl.imsglobal.org/spec/lti/claim/custom": {},
        "errors": {"errors": {}},
        "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
            "scope": [
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/score",
            ],
            "lineitems": "https://illumidesk.instructure.com/api/lti/courses/147/line_items",
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "picture": "https://canvas.instructure.com/images/messages/avatar-50.png",
        "email": "foo@example.com",
        "name": "Foo Bar",
        "given_name": "Foo",
        "family_name": "Bar",
        "https://purl.imsglobal.org/spec/lti/claim/lis": {
            "person_sourcedid": None,
            "course_offering_sourcedid": None,
            "validation_context": None,
            "errors": {"errors": {}},
        },
        "https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice": {
            "context_memberships_url": "https://illumidesk.instructure.com/api/lti/courses/147/names_and_roles",
            "service_versions": [
                "2.0",
            ],  # noqa: E231
            "validation_context": None,
            "errors": {"errors": {}},
        },  # noqa: E231
    }
    return jws


@pytest.fixture(scope="function")
def make_lti13_platform_jwks() -> Dict[str, List[Dict[str, str]]]:
    def _make_lti13_platform_jwks():
        """
        Valid response when retrieving jwks from the platform.
        """
        jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "e": "AQAB",
                    "n": "sBrymOqJsg3huJMJmmYi7kSQX5IPPFJokfZaFPCM87TDBtjvV_ha_i_wJYDGoiqM3GKY-h1PditDxpMrqUOwKoIYXYySKurdAQr_G2pmkkdFtX0FDclgzjJyioElpgzrZdgy4y5TaW-HOOCaW7fFFOArkCkwqdAdxXRH4daLQCX0QyAPbgZPigsWbMm9DnQlBYIfkDVAf0kmiOvWsYOvuEMbapgZC5meW6XcNRQ2goEp6RJWF5SQ0ZTI64rxFG2FiGpqF4LyzgtP1th4qBKMTyKFfiHn0CA_LBIaZ90_htR6onTKgYr8v4TREJkdLyu7tyrSZjfUYCTdzkLFT9_dXQ",
                    "kid": "2020-03-01T00:00:01Z",
                    "alg": "RS256",
                    "use": "sig",
                },
                {
                    "kty": "RSA",
                    "e": "AQAB",
                    "n": "7AugnfFImg9HWNN1gfp-9f0Qx26ctPMVGj4BmKdknP2wnVWQPn7jvYl6J0H7YZY40adSePU-urJ2ICQnVyJjKu9DPNOvWanB-hG96zhf_6wsU8rZJhXwfJzM-K7xhd7f0pf0VFG7HZAJXFazoPkCTLpdQ_daNVp7jklhz2qzBe0Y_cIZaCqfAWMI7M046kYKkvk87rPkwi75O3sOqF7GmOIWCHqNzt3p69gPeYOirin9XeAEL9ZmTwgtVHSXM8W1sLCnTEukRLuuAZzTjC79B7TwEqDu5kXI7MuOHOueX3ePKjulXwRDVxK4JyuT0XPBe6xrFbh9hXBK9SB3XY33mw",
                    "kid": "2020-04-01T00:00:04Z",
                    "alg": "RS256",
                    "use": "sig",
                },
                {
                    "kty": "RSA",
                    "e": "AQAB",
                    "n": "x5bJTy70O2XAMGVYq7ahfHZC6yovIfrH9pglFare2icDKVGA7u-9Fdruuma4lwwhRg6d7H3avZLY392zJKJByVkjNEfl0tszhbJ99jWoIzhvPNlk0_tCo1_9oCGEjZgh1wB8wVJIDm-Rt6ar5JwYNBGqPXbjWZTVRm5w9GccqLuK7Bc9RBecmU-WI1_pbWyz0T2I-9kn39K0u4Xhv3zTrZg_mkGsTNsVpBKkSSlHJnxsxq2_0v6TYNtzVmp2s7G11V3Ftp1gRQNaZcP2cEKISTip_Zj-bp63n8LaqH52Go1Jt7d1YFUSVth2OeWg4PURel8RIW5d0XwyaVVGbDMR2Q",
                    "kid": "2020-05-01T00:00:01Z",
                    "alg": "RS256",
                    "use": "sig",
                },
            ]
        }
        return jwks

    return _make_lti13_platform_jwks


@pytest.fixture(scope="function")
def make_lti13_resource_link_request_privacy_enabled(
    make_lti13_resource_link_request,
) -> Dict[str, str]:
    """
    Returns valid json after decoding JSON Web Token (JWT) for resource link launch (core)
    when Privacy is enabled.
    """
    del make_lti13_resource_link_request["picture"]
    del make_lti13_resource_link_request["email"]
    del make_lti13_resource_link_request["given_name"]
    del make_lti13_resource_link_request["family_name"]
    del make_lti13_resource_link_request[
        "https://purl.imsglobal.org/spec/lti/claim/lis"
    ]
    return make_lti13_resource_link_request


@pytest.fixture(scope="function")
def build_lti13_jwt_id_token(json_lti13_launch_request: Dict[str, str]) -> jwt:
    """
    Thin wrapper for the jwt.encode() method. Use the `make_lti13_resource_link_request`
    or `make_lti13_resource_link_request_privacy_enabled` fixture to create the json and
    then call this method to get the JWT.

    Args:
      json_lti13_launch_request (Dict[str, str]): the dictionary with claims/values that represents the
        decoded JWT payload.

    Returns: A JSON Web Token
    """
    encoded_jwt = jwt.encode(json_lti13_launch_request, "secret", algorithm="HS256")
    return encoded_jwt


@pytest.fixture
def pem_file(tmp_path):
    """
    Create a test private key file used with LTI 1.3 request/reponse flows
    """
    key = RSA.generate(2048)
    key_path = f"{tmp_path}/private.key"
    with open(key_path, "wb") as content_file:
        content_file.write(key.exportKey("PEM"))
    return key_path
