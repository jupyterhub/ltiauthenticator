"""
These fixtures are not used but kept as they may be relevant to use in the
future.
"""
import textwrap
from typing import Dict, List

import pytest


@pytest.fixture
def login_req_decoded():
    """
    A dictionary representing an initial login request.
    """
    return {
        "client_id": ["125900000000000085"],
        "iss": [
            "https://platform.vendor.com",
        ],
        "login_hint": [
            "185d6c59731a553009ca9b59ca3a885104ecb4ad",
        ],
        "target_link_uri": [
            "https://edu.example.com/hub",
        ],
        "lti_message_hint": [
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2ZXJpZmllciI6IjFlMjk2NjEyYjZmMjdjYmJkZTg5YmZjNGQ1ZmQ5ZDBhMzhkOTcwYzlhYzc0NDgwYzdlNTVkYzk3MTQyMzgwYjQxNGNiZjMwYzM5Nzk1Y2FmYTliOWYyYTgzNzJjNzg3MzAzNzAxZDgxMzQzZmRmMmIwZDk5ZTc3MWY5Y2JlYWM5IiwiY2FudmFzX2RvbWFpbiI6ImlsbHVtaWRlc2suaW5zdHJ1Y3R1cmUuY29tIiwiY29udGV4dF90eXBlIjoiQ291cnNlIiwiY29udGV4dF9pZCI6MTI1OTAwMDAwMDAwMDAwMTM2LCJleHAiOjE1OTE4MzMyNTh9.uYHinkiAT5H6EkZW9D7HJ1efoCmRpy3Id-gojZHlUaA",
        ],
    }


@pytest.fixture
def jwks_endpoint_response() -> Dict[str, List[Dict[str, str]]]:
    """
    This is a response from with references to public keys
    https://lti-ri.imsglobal.org/platforms/3691/platform_keys/3396.json, where
    the associated private key has been used to sign the launch_request_jwk
    token.

    Currently, our tests make use of this endpoint directly instead of mocking
    its response in test_validate_verify_and_decode_jwt, which makes it a bit
    error prone as we rely on an external service.
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
