"""
These fixtures are not used but kept as they may be relevant to use in the
future.
"""
from typing import Any, Callable, Dict

import jwt
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
def id_token(json_lti13_launch_request: Dict[str, str]) -> str:
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
def get_id_token() -> Callable[[Dict[str, str]], Any]:
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
