import os
import textwrap
from calendar import timegm
from datetime import datetime, timezone
from typing import Dict, List
from unittest.mock import Mock

import jwt
import pytest
from tornado.httputil import HTTPServerRequest
from tornado.web import Application, RequestHandler


@pytest.fixture
def now() -> int:
    return timegm(datetime.now(tz=timezone.utc).utctimetuple())


@pytest.fixture
def req_handler() -> RequestHandler:
    """
    Sourced from https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/tests/mocks.py
    """

    def _req_handler(
        Handler,
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
        request = HTTPServerRequest(method=method, uri=uri, connection=Mock())
        handler = Handler(
            application=application,
            request=request,
        )
        handler._transforms = []
        return handler

    return _req_handler


@pytest.fixture
def launch_req_jwt(
    launch_req_jwt_decoded, jwks_endpoint_private_key, jwks_endpoint_response
):
    """
    Returns an encoded JSON Web Token (JWT) for the authenticate request
    (resource link launch). This decodes into the launch_req_jwt_decoded
    fixture.
    """
    encoded = jwt.encode(
        launch_req_jwt_decoded,
        jwks_endpoint_private_key,
        algorithm="RS256",
        headers={
            "alg": jwks_endpoint_response["keys"][0]["alg"],
            "kid": jwks_endpoint_response["keys"][0]["kid"],
        },
    )
    return encoded.encode("utf-8")
    # return b"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IlVpNVpkcDlNcUVZQ2VyQ3E4ejhRUVQ4MWpna24zeDNKWWMwNk9vckY4TW8ifQ.eyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9tZXNzYWdlX3R5cGUiOiJMdGlSZXNvdXJjZUxpbmtSZXF1ZXN0IiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vcm9sZXMiOlsiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvbWVtYmVyc2hpcCNMZWFybmVyIiwiaHR0cDovL3B1cmwuaW1zZ2xvYmFsLm9yZy92b2NhYi9saXMvdjIvaW5zdGl0dXRpb24vcGVyc29uI1N0dWRlbnQiLCJodHRwOi8vcHVybC5pbXNnbG9iYWwub3JnL3ZvY2FiL2xpcy92Mi9tZW1iZXJzaGlwI01lbnRvciJdLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9yb2xlX3Njb3BlX21lbnRvciI6WyJhNjJjNTJjMDJiYTI2MjAwM2Y1ZSJdLCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS9jbGFpbS9yZXNvdXJjZV9saW5rIjp7ImlkIjoiNzQyNTYiLCJ0aXRsZSI6ImxpbmsxIiwiZGVzY3JpcHRpb24iOiIifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY29udGV4dCI6eyJpZCI6IjU0NTM2IiwibGFiZWwiOiJjb3Vyc2UxIiwidGl0bGUiOiJjb3Vyc2UxIiwidHlwZSI6WyIiXX0sImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3Rvb2xfcGxhdGZvcm0iOnsibmFtZSI6Imp1cHl0ZXJodWItbHRpYXV0aGVudGljYXRvci10ZXN0LXBsYXRmb3JtIiwiY29udGFjdF9lbWFpbCI6IiIsImRlc2NyaXB0aW9uIjoiIiwidXJsIjoiIiwicHJvZHVjdF9mYW1pbHlfY29kZSI6IiIsInZlcnNpb24iOiIxLjAiLCJndWlkIjoiMzY5MSJ9LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1hZ3MvY2xhaW0vZW5kcG9pbnQiOnsic2NvcGUiOlsiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL2xpbmVpdGVtIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktYWdzL3Njb3BlL3Jlc3VsdC5yZWFkb25seSIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpLWFncy9zY29wZS9zY29yZSJdLCJsaW5laXRlbXMiOiJodHRwczovL2x0aS1yaS5pbXNnbG9iYWwub3JnL3BsYXRmb3Jtcy8zNjkxL2NvbnRleHRzLzU0NTM2L2xpbmVfaXRlbXMifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGktbnJwcy9jbGFpbS9uYW1lc3JvbGVzZXJ2aWNlIjp7ImNvbnRleHRfbWVtYmVyc2hpcHNfdXJsIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9wbGF0Zm9ybXMvMzY5MS9jb250ZXh0cy81NDUzNi9tZW1iZXJzaGlwcyIsInNlcnZpY2VfdmVyc2lvbnMiOlsiMi4wIl19LCJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1jZXMvY2xhaW0vY2FsaXBlci1lbmRwb2ludC1zZXJ2aWNlIjp7InNjb3BlcyI6WyJodHRwczovL3B1cmwuaW1zZ2xvYmFsLm9yZy9zcGVjL2x0aS1jZXMvdjFwMC9zY29wZS9zZW5kIl0sImNhbGlwZXJfZW5kcG9pbnRfdXJsIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9wbGF0Zm9ybXMvMzY5MS9zZW5zb3JzIiwiY2FsaXBlcl9mZWRlcmF0ZWRfc2Vzc2lvbl9pZCI6InVybjp1dWlkOjk0YzNhOTRjYTcwNjQ3ZDA4ZTdjIn0sImlzcyI6Imh0dHBzOi8vZ2l0aHViLmNvbS9qdXB5dGVyaHViL2x0aWF1dGhlbnRpY2F0b3IiLCJhdWQiOiJjbGllbnQxIiwiaWF0IjoxNjY4MjY2NTU1LCJleHAiOjE2NjgyNjY4NTUsInN1YiI6IjFhY2U3NTAxODc3ZTZhNDI5ZmNhIiwibm9uY2UiOiJlYmM5YWI3MDVkMGJhYjNlOWRjNiIsImh0dHBzOi8vcHVybC5pbXNnbG9iYWwub3JnL3NwZWMvbHRpL2NsYWltL3ZlcnNpb24iOiIxLjMuMCIsImxvY2FsZSI6ImVuLVVTIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vbGF1bmNoX3ByZXNlbnRhdGlvbiI6eyJkb2N1bWVudF90YXJnZXQiOiJpZnJhbWUiLCJoZWlnaHQiOjMyMCwid2lkdGgiOjI0MCwicmV0dXJuX3VybCI6Imh0dHBzOi8vbHRpLXJpLmltc2dsb2JhbC5vcmcvcGxhdGZvcm1zLzM2OTEvcmV0dXJucyJ9LCJodHRwczovL3d3dy5leGFtcGxlLmNvbS9leHRlbnNpb24iOnsiY29sb3IiOiJ2aW9sZXQifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vY3VzdG9tIjp7Im15Q3VzdG9tVmFsdWUiOiIxMjMifSwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vZGVwbG95bWVudF9pZCI6ImRlcGxveW1lbnQxIiwiaHR0cHM6Ly9wdXJsLmltc2dsb2JhbC5vcmcvc3BlYy9sdGkvY2xhaW0vdGFyZ2V0X2xpbmtfdXJpIjoiaHR0cHM6Ly9sdGktcmkuaW1zZ2xvYmFsLm9yZy9sdGkvdG9vbHMvMzM1Ni9sYXVuY2hlcyJ9.fTmEDNdk3RICex0fdpFVHvActISqURZiYWc-JmV7CTBQ1D9bcB7ovK-Nf2qDz6cfGCCOWv-3QJzJliEvmgBeYclGgnX39IXQQ49TiWrkoQJsPCpnrxqheWlvK0Aceca0zxnncc2yV8IyXe0UiwzZFyExwcbNUhgeLFyPBvIH5zl7LzMwlywhl8qKGcOxW__yTQ9dRID6y5KFOMzkXzHKzuJW4D0RpqkAkpX2QD4KraIGJkEb_qQSwjA5BbtgsCi2fF3wBxBNUDLaKpr2iYoENSXvO4yoQ20US5BC2E8mOf4RpkPlC1AyqXV9gqOWzw07x3NDXQgsfsqFcVTC6G4Z5Q"


@pytest.fixture
def unsecured_launch_req_jwt(launch_req_jwt):
    """Return unsecured launch request."""
    unsigned_jwt = launch_req_jwt.split(b".")
    unsigned_jwt[2:] = b""
    unsigned_jwt = b".".join(unsigned_jwt) + b"."
    return unsigned_jwt


@pytest.fixture
def minimal_launch_req_jwt_decoded(now) -> Dict[str, object]:
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
        "iat": now - 30,
        "exp": now + 300,
        "nonce": "ebc9ab705d0bab3e9dc6",
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
def jwks_endpoint_response() -> Dict[str, List[Dict[str, str]]]:
    """
    This is a response from with references to public keys
    https://lti-ri.imsglobal.org/platforms/3691/platform_keys/3396.json, where
    the associated private key has been used to sign the launch_request_jwk
    token.
    """
    return {
        "keys": [
            {
                "kty": "RSA",
                "e": "AQAB",
                "n": "nVhjh6rQNuXmbe5t-bacRizy0aE4pdL_MchSvA_m0Wmnp6D7rSGrzwqAOUBN0gcXfj-2ILgZffESJcPugVzEoDPuXgMkywLLcnTt9MVWB8jWrSECOCUO5mLzqaSJRw1tpSnBstlq0A2JCIPL1g62XhM4ilquz-uOLYv4J50R0OUqz1q79vSmK9yjcl16jqntGTHsMAC_1x3HGzmyACjAI-DjR5m0qKLDUsb6PF8x7EK4_d2jBjsHW_ymG7BMP_ZwJ3EA4oo2mUCsjQWpKo8cgDDx4B7OA8Or90hb-gU3qoAcRcou_aUGZ96EWuuYGlxf6mb3z3KQRsJeM7gdMPMgYQ",
                "kid": "Ui5Zdp9MqEYCerCq8z8QQT81jgkn3x3JYc06OorF8Mo",
                "alg": "RS256",
                "use": "sig",
            }
        ],
    }


@pytest.fixture
def jwks_endpoint_public_key():
    """
    The jwks_endpoint_response fixture provides a single key (public), and this
    is the same public key.
    """
    return textwrap.dedent(
        """
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVhjh6rQNuXmbe5t+bac
        Rizy0aE4pdL/MchSvA/m0Wmnp6D7rSGrzwqAOUBN0gcXfj+2ILgZffESJcPugVzE
        oDPuXgMkywLLcnTt9MVWB8jWrSECOCUO5mLzqaSJRw1tpSnBstlq0A2JCIPL1g62
        XhM4ilquz+uOLYv4J50R0OUqz1q79vSmK9yjcl16jqntGTHsMAC/1x3HGzmyACjA
        I+DjR5m0qKLDUsb6PF8x7EK4/d2jBjsHW/ymG7BMP/ZwJ3EA4oo2mUCsjQWpKo8c
        gDDx4B7OA8Or90hb+gU3qoAcRcou/aUGZ96EWuuYGlxf6mb3z3KQRsJeM7gdMPMg
        YQIDAQAB
        -----END PUBLIC KEY-----
        """
    ).strip()


@pytest.fixture
def jwks_endpoint_private_key():
    """
    The jwks_endpoint_response fixture provides a single key (public), and this
    is the private key behind it. This fixture could be used to sign a JWT if
    needed for our tests.
    """
    return textwrap.dedent(
        """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEAnVhjh6rQNuXmbe5t+bacRizy0aE4pdL/MchSvA/m0Wmnp6D7
        rSGrzwqAOUBN0gcXfj+2ILgZffESJcPugVzEoDPuXgMkywLLcnTt9MVWB8jWrSEC
        OCUO5mLzqaSJRw1tpSnBstlq0A2JCIPL1g62XhM4ilquz+uOLYv4J50R0OUqz1q7
        9vSmK9yjcl16jqntGTHsMAC/1x3HGzmyACjAI+DjR5m0qKLDUsb6PF8x7EK4/d2j
        BjsHW/ymG7BMP/ZwJ3EA4oo2mUCsjQWpKo8cgDDx4B7OA8Or90hb+gU3qoAcRcou
        /aUGZ96EWuuYGlxf6mb3z3KQRsJeM7gdMPMgYQIDAQABAoIBAEXU2qd1ed9DfVdA
        wHJZR1Yl0MaUxO1jjXrsqztn20sJlyzgV5JpJTVINcwy69bQ6u5PHGe9DSNGAIXe
        RVYIdAOdyKbUwlmPLffoSUue4SWnTw+bXL7KQ6igNgAOVBbCsOzicWMM90jLGQw8
        YhTohquN4EQXJwqEQp+YRVRfc26/9E7Geo1/47PlcEkPEoiS12etwg1/iLF8x+vQ
        JLYt0vWd3iIpnYQ+sIuUat3aM4CYe8TmmU7nDYFMV9g84gDwST3aA19mrY2ukWWh
        3GkEz44jLzZUHCZMLP/LyBBflctlzmZuYstL6fayyGNClYOnLgPPdhCS9tWJAm0a
        aqq47gECgYEA0IWXbzoVGNWLreJdSkTeV1Vu3fegA04DPzFCk52v446n6Pz41LzY
        Cn/Le8Fnd21+bmZnlfI1/RSiGeGbt0zQEhpElTuwpJLtkMTD3nJ7CfegQTcsgFjw
        8E4iYyPPqeaLrp430NHNzcCAJM0ZuWkh6YNIKtkzs97y5M/BReeleTECgYEAwSvL
        s8kn/s7MbMPz58RjSaCUuhWmnlrmhPOO8I+wfp+H11lvSjoEhe58xC+MEwx4hmT0
        eUm9o4/zHsi6fNpYQKu/ZQDD8hA3aNim4qa/EAaGifSOphVafkwKEpIowUNZ28JS
        Q8CCWKaNZhoW3eFmzqxJeKk0tZGncgOLmw56TjECgYEArsKn7lJRiCTBEhSbdzlM
        1wkFCAcXFm31jqqsT6di2GahF0WdDj7PGc2NLsUjABbGVaSBwEvlL5xxVxucM/2u
        jN1zCVejbequLBycw/xSXkIpDz88jrz8AYqai1hiHNTZ0JlN0jdkMsLZIv66Roh0
        IY8jlrW+/Usnatkr9Hh2WKECgYEAp+kw1SNqn6QUsAqYzgK4p3xtK1+8iHPNYw3v
        Vw4fxcFYLAnyohvSaLUIQORvpvM1JOVGWNOPg0iSdVTYPcTx560i3mIO8S/Fal7A
        mc2F0SFK+0nYYWe4VIY2TzQ7NtsbldnQ9lG1O+fyiyjsbYwLeGTsLHUwew+T9Jg+
        Vtb721ECgYAPr9YYRP0P+Bif/T4h8tLMjnSoyv6G8101s63lLzv+CtjbOrYvvemS
        IrcmoDaFnFXWbWr5iVcyWnj+RI1h5NqDqKgW0TXOOManSBKlTuJdaeOiBFNK47kz
        RgKGvGteNRDxt0GjIrzdx5xaf4/ve0UjPU0z+fRrRBuij8V0/pscSA==
        -----END RSA PRIVATE KEY-----
        """
    ).strip()
