import uuid
import json
import jwt
import logging
import pem
import os
import re
import time
import urllib

from Crypto.PublicKey import RSA
from jwcrypto.jwk import JWK

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
from tornado.web import RequestHandler

from typing import Any
from typing import Dict
from typing import List

from ltiauthenticator.lti13.constants import DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR
from ltiauthenticator.lti13.constants import DEFAULT_ROLE_NAMES_FOR_STUDENT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def normalize_string(name: str) -> str:
    """
    Function used to strip special characters and convert strings
    to docker container compatible names. This function is used mostly
    with course labels, as they are used for the shared grader notebook
    container names.

    Args:
        name: The string to normalize for docker container and volume
        names (e.g. Dev-JupyterHub)

    Returns:
        normalized_name: The normalized string
    """
    if not name:
        raise ValueError("Name is empty")
    # truncate name after 30th character
    name = (name[:25] + "") if len(name) > 30 else name
    # remove special characters
    name = re.sub(r"[^\w-]+", "", name)
    # if the first character is any of _.- remove it
    name = name.lstrip("_.-")
    # convert to lower case
    name = name.lower()
    # limit course_id to 25 characters, since its used for o/s username
    # in jupyter/docker-stacks compatible grader notebook (NB_USER)
    normalized_name = name[0:25]
    logger.debug("String normalized to %s" % normalized_name)
    return normalized_name


def email_to_username(email: str) -> str:
    """
    Normalizes an email to get a username. This function
    calculates the username by getting the string before the
    @ symbol, removing special characters, removing comments,
    converting string to lowercase, and adds 1 if the username
    has an integer value already in the string.

    Args:
        email: A valid email address

    Returns:
        username: A username string

    Raises:
        ValueError if email is empty
    """
    if not email:
        raise ValueError("email is missing")
    username = email.split("@")[0]
    username = username.split("+")[0]
    username = re.sub(r"\([^)]*\)", "", username)
    username = re.sub(r"[^\w-]+", "", username)
    username = username.lower()
    logger.debug("Username normalized to %s" % username)

    return username


def get_client_protocol(handler: RequestHandler) -> Dict[str, str]:
    """
    This is a copy of the jupyterhub-ltiauthenticator logic to get the first
    protocol value from the x-forwarded-proto list, assuming there is more than
    one value. Otherwise, this returns the value as-is.

    Extracted as a method to facilitate testing.

    Args:
        handler: a tornado.web.RequestHandler object

    Returns:
        A decoded dict with keys/values extracted from the request's arguments
    """
    if "x-forwarded-proto" in handler.request.headers:
        hops = [
            h.strip() for h in handler.request.headers["x-forwarded-proto"].split(",")
        ]
        protocol = hops[0]
    else:
        protocol = handler.request.protocol

    return protocol


def convert_request_to_dict(arguments: Dict[str, List[bytes]]) -> Dict[str, Any]:
    """
    Converts the arguments obtained from a request to a dict.

    Args:
        handler: a tornado.web.RequestHandler object

    Returns:
        A decoded dict with keys/values extracted from the request's arguments
    """
    args = {}
    for k, values in arguments.items():
        args[k] = values[0].decode()
    return args


async def get_lms_access_token(
    token_endpoint: str, private_key_path: str, client_id: str, scope=None
) -> str:
    """
    Gets an access token from the LMS Token endpoint by using the private key (pem format) and client id

    Args:
        token_endpoint: The url that will be used to make the request
        private_key_path: specify where the pem is
        client_id: For LTI 1.3 the Client ID that was obtained with the tool setup

    Returns:
        A json with the token value
    """
    token_params = {
        "iss": client_id,
        "sub": client_id,
        "aud": token_endpoint,
        "iat": int(time.time()) - 5,
        "exp": int(time.time()) + 60,
        "jti": str(uuid.uuid4()),
    }
    logger.debug("Getting LTI 1.3 access token with parameters %s" % token_params)
    # get the pem-encoded content
    private_key = get_pem_text_from_file(private_key_path)

    headers = get_headers_to_jwt_encode(private_key)

    token = jwt.encode(token_params, private_key, algorithm="RS256", headers=headers)
    logger.debug("Obtaining LTI 1.3 token %s" % token)
    scope = scope or " ".join(
        [
            "https://purl.imsglobal.org/spec/lti-ags/scope/score",
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
            "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
        ]
    )
    logger.debug("LTI 1.3 Scope is %s" % scope)
    params = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": token.decode(),
        "scope": scope,
    }
    logger.debug("LTI 1.3 OAuth parameters are %s" % params)
    client = AsyncHTTPClient()
    body = urllib.parse.urlencode(params)
    try:
        resp = await client.fetch(
            token_endpoint, method="POST", body=body, headers=None
        )
    except HTTPClientError as e:
        logger.info(
            f"Error by obtaining a token with lms. Detail: {e.response.body if e.response else e.message}"
        )
        raise
    logger.debug("Token response body is %s" % json.loads(resp.body))
    return json.loads(resp.body)


def get_jwk(public_key):
    """Gets the JSON Web Key"""

    jwk_obj = JWK.from_pem(public_key)
    public_jwk = json.loads(jwk_obj.export_public())
    public_jwk["alg"] = "RS256"
    public_jwk["use"] = "sig"
    return public_jwk


def get_headers_to_jwt_encode(private_key_text: str) -> dict:
    """
    Helper method that gets the dict headers to use in jwt.encode method

    Args:
      private_key_text: The PEM-Encoded content as text

    Returns:
      A dict if the publickey can be exported or None otherwise
    """
    public_key = RSA.importKey(private_key_text).publickey().exportKey()
    headers = None
    if public_key:
        jwk = get_jwk(public_key)
        headers = {"kid": jwk.get("kid")} if jwk else None

    return headers


def get_pem_text_from_file(private_key_path: str) -> str:
    """
    Parses the pem file to get its value as unicode text

    Args:
      private_key_path: absolute file system path for pem key file.

    Returns:
      String representation of PEM key.
    """
    # check the pem file permission
    if not os.access(private_key_path, os.R_OK):
        raise PermissionError()
    # parse file generates a list of PEM objects
    certs = pem.parse_file(private_key_path)
    if not certs:
        raise Exception("Invalid pem file.")

    return certs[0].as_text()


def user_is_a_student(user_role: str) -> str:
    """Determins if the user has a Student/Learner role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case student string
    """
    if not user_role:
        raise ValueError('user_role must have a value')
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_STUDENT


def user_is_an_instructor(user_role: str) -> str:
    """Determins if the user has a Instructor/Teacher role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case instructor string
    """
    if not user_role:
        raise ValueError('user_role must have a value')
    # find the extra role names to recognize an instructor (to be added in the grader group)
    extra_roles = os.environ.get('EXTRA_ROLE_NAMES_FOR_INSTRUCTOR') or []
    if extra_roles:
        extra_roles = extra_roles.lower().split(',')
        DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR.extend(extra_roles)
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR
