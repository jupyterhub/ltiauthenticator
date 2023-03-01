import os
from typing import Dict
from unittest.mock import Mock

import jwt
import pytest
from tornado.httputil import HTTPServerRequest
from tornado.web import Application, RequestHandler


@pytest.fixture
def req_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
    """

    def _req_handler(
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

    return _req_handler


@pytest.fixture
def launch_req_jwt():
    """
    Returns an encoded JSON Web Token (JWT) for the authenticate request
    (resource link launch). This decodes into the launch_req_jwt_decoded
    fixture, but if jwt.decode is used, you need to use options={"verify_exp":
    False} at this point as the expiry time has since long passed.
    """
    return b"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IlVpNVpkcDlNcUVZQ2VyQ3E4ejhRUVQ4MWpna24zeDNKWWMwNk9vckY4TW8ifQ.eyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9tZXNzYWdlX3R5cGUiOiJMdGlSZXNvdXJjZUxpbmtSZXF1ZXN0IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vcm9sZXMiOlsiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvbWVtYmVyc2hpcCNMZWFybmVyIiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvaW5zdGl0dXRpb24vcGVyc29uI1N0dWRlbnQiLCJodHRwOi8vcHVybC5pbXNnbG9iYWwub3JnL3ZvY2FiL2xpcy92Mi9tZW1iZXJzaGlwI01lbnRvciJdLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9yb2xlX3Njb3BlX21lbnRvciI6WyJhNjJjNTJjMDJiYTI2MjAwM2Y1ZSJdLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9yZXNvdXJjZV9saW5rIjp7ImlkIjoiNzQyNTYiLCJ0aXRsZSI6ImxpbmsxIiwiZGVzY3JpcHRpb24iOiIifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY29udGV4dCI6eyJpZCI6IjU0NTM2IiwibGFiZWwiOiJjb3Vyc2UxIiwidGl0bGUiOiJjb3Vyc2UxIiwidHlwZSI6WyIiXX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3Rvb2xfcGxhdGZvcm0iOnsibmFtZSI6Imp1cHl0ZXJodWItbHRpYXV0aGVudGljYXRvci10ZXN0LXBsYXRmb3JtIiwiY29udGFjdF9lbWFpbCI6IiIsImRlc2NyaXB0aW9uIjoiIiwidXJsIjoiIiwicHJvZHVjdF9mYW1pbHlfY29kZSI6IiIsInZlcnNpb24iOiIxLjAiLCJndWlkIjoiMzY5MSJ9LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3MvY2xhaW0vZW5kcG9pbnQiOnsic2NvcGUiOlsiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL2xpbmVpdGVtIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL3Jlc3VsdC5yZWFkb25seSIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLWFncy9zY29wZS9zY29yZSJdLCJsaW5laXRlbXMiOiJodHRwczovL2x0aS1yaS5pbXNnbG9iYWwub3JnL3BsYXRmb3Jtcy8zNjkxL2NvbnRleHRzLzU0NTM2L2xpbmVfaXRlbXMifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktbnJwcy9jbGFpbS9uYW1lc3JvbGVzZXJ2aWNlIjp7ImNvbnRleHRfbWVtYmVyc2hpcHNfdXJsIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9wbGF0Zm9ybXMvMzY5MS9jb250ZXh0cy81NDUzNi9tZW1iZXJzaGlwcyIsInNlcnZpY2VfdmVyc2lvbnMiOlsiMi4wIl19LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1jZXMvY2xhaW0vY2FsaXBlci1lbmRwb2ludC1zZXJ2aWNlIjp7InNjb3BlcyI6WyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1jZXMvdjFwMC9zY29wZS9zZW5kIl0sImNhbGlwZXJfZW5kcG9pbnRfdXJsIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9wbGF0Zm9ybXMvMzY5MS9zZW5zb3JzIiwiY2FsaXBlcl9mZWRlcmF0ZWRfc2Vzc2lvbl9pZCI6InVybjp1dWlkOjk0YzNhOTRjYTcwNjQ3ZDA4ZTdjIn0sImlzcyI6Imh0dHBzOi8vZ2l0aHViLmNvbS9qdXB5dGVyaHViL2x0aWF1dGhlbnRpY2F0b3IiLCJhdWQiOiJjbGllbnQxIiwiaWF0IjoxNjY4MjY2NTU1LCJleHAiOjE2NjgyNjY4NTUsInN1YiI6IjFhY2U3NTAxODc3ZTZhNDI5ZmNhIiwibm9uY2UiOiJlYmM5YWI3MDVkMGJhYjNlOWRjNiIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3ZlcnNpb24iOiIxLjMuMCIsImxvY2FsZSI6ImVuLVVTIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vbGF1bmNoX3ByZXNlbnRhdGlvbiI6eyJkb2N1bWVudF90YXJnZXQiOiJpZnJhbWUiLCJoZWlnaHQiOjMyMCwid2lkdGgiOjI0MCwicmV0dXJuX3VybCI6Imh0dHBzOi8vbHRpLXJpLmltc2dsb2JhbC5vcmcvcGxhdGZvcm1zLzM2OTEvcmV0dXJucyJ9LCJodHRwczovL3d3dy5leGFtcGxlLmNvbS9leHRlbnNpb24iOnsiY29sb3IiOiJ2aW9sZXQifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY3VzdG9tIjp7Im15Q3VzdG9tVmFsdWUiOiIxMjMifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vZGVwbG95bWVudF9pZCI6ImRlcGxveW1lbnQxIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdGFyZ2V0X2xpbmtfdXJpIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9sdGkvdG9vbHMvMzM1Ni9sYXVuY2hlcyJ9.fTmEDNdk3RICex0fdpFVHvActISqURZiYWc-JmV7CTBQ1D9bcB7ovK-Nf2qDz6cfGCCOWv-3QJzJliEvmgBeYclGgnX39IXQQ49TiWrkoQJsPCpnrxqheWlvK0Aceca0zxnncc2yV8IyXe0UiwzZFyExwcbNUhgeLFyPBvIH5zl7LzMwlywhl8qKGcOxW__yTQ9dRID6y5KFOMzkXzHKzuJW4D0RpqkAkpX2QD4KraIGJkEb_qQSwjA5BbtgsCi2fF3wBxBNUDLaKpr2iYoENSXvO4yoQ20US5BC2E8mOf4RpkPlC1AyqXV9gqOWzw07x3NDXQgsfsqFcVTC6G4Z5Q"


@pytest.fixture
def minimal_launch_req_jwt_decoded() -> Dict[str, object]:
    """
    Returns valid json after decoding JSON Web Token (JWT) for resource link launch (core).

    Only contains message claims flagged as required by the LTI 1.3 specs.
    https://www.imsglobal.org/spec/lti/v1p3#required-message-claims
    """
    jwt_decoded = {
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "deployment1",
        "https://purl.imsglobal.org/spec/lti/claim/target_link_uri": "https://lti-ri.imsglobal.org/lti/tools/3356/launches",
        "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
            "id": "74256",
        },
        "https://purl.imsglobal.org/spec/lti/claim/roles": [],
        # Required OAuth2 claims
        # https://www.imsglobal.org/spec/security/v1p0/#using-oauth-2-0-client-credentials-grant
        "iss": "https://github.com/jupyterhub/ltiauthenticator",
        "aud": "client1",
        "iat": 1668266555,
        "exp": 1668266855,
    }
    return jwt_decoded


@pytest.fixture
def launch_req_jwt_decoded(minimal_launch_req_jwt_decoded) -> Dict[str, str]:
    """
    Returns a decoded JSON Web Token (JWT) for the authenticate request
    (resource link launch).
    """
    # This example data was generated via
    # https://lti-ri.imsglobal.org/platforms/3691 and
    # https://lti-ri.imsglobal.org/lti/tools/3356 by clicking around.
    #
    # This example data is provided via:
    # https://lti-ri.imsglobal.org/platforms/3691/resource_links/74256?nonce=ebc9ab705d0bab3e9dc6&redirect_uri=https%3A%2F%2Flti-ri.imsglobal.org%2Flti%2Ftools%2F3356%2Flaunches&tool_state=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjNyNlRqNW9JbWw2cW9VcnBIcWh1NjJsY0N1OW9qTzNKYXAyTFpuTnIybWsiLCJ0eXAiOiJKV1QifQ.eyJ0b29sX2lkIjozMzU2LCJzdGF0ZV9ub25jZSI6ImViYzlhYjcwNWQwYmFiM2U5ZGM2IiwicGFyYW1zIjp7InV0ZjgiOiLinJMiLCJpc3MiOiJodHRwczovL2dpdGh1Yi5jb20vanVweXRlcmh1Yi9sdGlhdXRoZW50aWNhdG9yIiwibG9naW5faGludCI6IjU0NDU2NCIsInRhcmdldF9saW5rX3VyaSI6Imh0dHBzOi8vbHRpLXJpLmltc2dsb2JhbC5vcmcvbHRpL3Rvb2xzLzMzNTYvbGF1bmNoZXMiLCJsdGlfbWVzc2FnZV9oaW50IjoiNzQyNTYiLCJsdGlfZGVwbG95bWVudF9pZCI6ImRlcGxveW1lbnQxIiwiY2xpZW50X2lkIjoiY2xpZW50MSIsImNvbW1pdCI6IlBvc3QgcmVxdWVzdCIsImNvbnRyb2xsZXIiOiJsdGkvbG9naW5faW5pdGlhdGlvbnMiLCJhY3Rpb24iOiJjcmVhdGUiLCJ0b29sX2lkIjoiMzM1NiJ9LCJpc3MiOiJqdXB5dGVyaHViLWx0aWF1dGhlbnRpY2F0b3ItdGVzdC10b29sIiwic3ViIjoiY2xpZW50MSIsImF1ZCI6Imh0dHBzOi8vbHRpLXJpLmltc2dsb2JhbC5vcmcvcGxhdGZvcm1zLzM2OTEvYWNjZXNzX3Rva2VucyIsImlhdCI6MTY2ODI2NjU1MCwiZXhwIjoxNjY4MjY2ODUwLCJqdGkiOiIyMmM1NjU1ZTNiMjFjNjdjOWYwNyJ9.VJa5KQEjekM7vmmgCLVUN1c6XBv-B-2nkvKzki-8m6XpZ4F2eBiwG2518wXKAEsttHDmWRnjd_d5DU1sOG3RP8XcybGe578o7bY2iSHkwrqlykBw5pvlg3MPpdY9VsdVL_SUTY5HMq8M8A2krfR82giI1Iy0a475d9d4rtZ7VLTCCxMadYIMo0SDZCmhHsF2QtfbYT3bsFh2LmrhsPEun80eLNYxwkrRLS633sAkNWmekhRqAUsPMmqocDUwxRxsDbbvmHpBRUO3cl8Dqbaxz52TVQtLl6rEi9gux4D83IHehC0Q5HKFU04WhXNo_XdHU_0IK7tXYw9uMw6CvKKhWg&user_id=544564
    #
    jwt_decoded = minimal_launch_req_jwt_decoded
    jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/roles"] = [
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
    ]
    jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/resource_link"].update(
        {"title": "link1", "description": ""}
    )
    jwt_decoded.update(
        {
            "https://purl.imsglobal.org/spec/lti/claim/role_scope_mentor": [
                "a62c52c02ba262003f5e"
            ],
            "https://purl.imsglobal.org/spec/lti/claim/context": {
                "id": "54536",
                "label": "course1",
                "title": "course1",
                "type": [""],
            },
            "https://purl.imsglobal.org/spec/lti/claim/tool_platform": {
                "name": "jupyterhub-ltiauthenticator-test-platform",
                "contact_email": "",
                "description": "",
                "url": "",
                "product_family_code": "",
                "version": "1.0",
                "guid": "3691",
            },
            "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
                "scope": [
                    "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                    "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                    "https://purl.imsglobal.org/spec/lti-ags/scope/score",
                ],
                "lineitems": "https://lti-ri.imsglobal.org/platforms/3691/contexts/54536/line_items",
            },
            "https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice": {
                "context_memberships_url": "https://lti-ri.imsglobal.org/platforms/3691/contexts/54536/memberships",
                "service_versions": ["2.0"],
            },
            "https://purl.imsglobal.org/spec/lti-ces/claim/caliper-endpoint-service": {
                "scopes": ["https://purl.imsglobal.org/spec/lti-ces/v1p0/scope/send"],
                "caliper_endpoint_url": "https://lti-ri.imsglobal.org/platforms/3691/sensors",
                "caliper_federated_session_id": "urn:uuid:94c3a94ca70647d08e7c",
            },
            "sub": "1ace7501877e6a429fca",
            "nonce": "ebc9ab705d0bab3e9dc6",
            "locale": "en-US",
            "https://purl.imsglobal.org/spec/lti/claim/launch_presentation": {
                "document_target": "iframe",
                "height": 320,
                "width": 240,
                "return_url": "https://lti-ri.imsglobal.org/platforms/3691/returns",
            },
            "https://www.example.com/extension": {
                "color": "violet",
            },
            "https://purl.imsglobal.org/spec/lti/claim/custom": {
                "myCustomValue": "123",
            },
        }
    )
    return jwt_decoded


@pytest.fixture
def launch_req_jwt_decoded_priv(launch_req_jwt_decoded) -> Dict[str, str]:
    """
    Returns a decoded JSON Web Token (JWT) for resource link launch (core). when
    Privacy is enabled.
    """
    launch_req_jwt_decoded.pop("picture", None)
    launch_req_jwt_decoded.pop("email", None)
    launch_req_jwt_decoded.pop("given_name", None)
    launch_req_jwt_decoded.pop("family_name", None)
    launch_req_jwt_decoded.pop("https://purl.imsglobal.org/spec/lti/claim/lis", None)
    return launch_req_jwt_decoded


@pytest.fixture
def id_token(json_lti13_launch_request: Dict[str, str]) -> jwt:
    """
    Thin wrapper for the jwt.encode() method. Use the `launch_req_jwt_decoded`
    or `launch_req_jwt_decoded_priv` fixture to create the json and
    then call this method to get the JWT.

    Args:
      json_lti13_launch_request (Dict[str, str]): the dictionary with claims/values that represents the
        decoded JWT payload.

    Returns: A JSON Web Token
    """
    encoded_jwt = jwt.encode(json_lti13_launch_request, "secret", algorithm="HS256")
    return encoded_jwt


@pytest.fixture
def get_id_token() -> str:
    def _get_id_token(json_lti13_launch_request: Dict[str, str]):
        """
        Returns a valid jwt lti13 id token from a json
        We can use the `launch_req_jwt_decoded` or `launch_req_jwt_decoded_priv`
        fixture to create the json then call this method.
        """
        encoded_jwt = jwt.encode(
            json_lti13_launch_request, "secret", algorithm="HS256"
        ).encode()
        return encoded_jwt

    return _get_id_token
