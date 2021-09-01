import json
import logging
import os
import time
import urllib
import uuid
from typing import Dict

import jwt
import pem
from Crypto.PublicKey import RSA
from jupyterhub.auth import LocalAuthenticator
from oauthenticator.oauth2 import OAuthenticator
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError
from tornado.web import HTTPError
from traitlets.config import Unicode

from ltiauthenticator.lti13.handlers import LTI13CallbackHandler
from ltiauthenticator.lti13.handlers import LTI13LoginHandler
from ltiauthenticator.lti13.validator import LTI13LaunchValidator
from ltiauthenticator.utils import get_jwk

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    logger.debug("Getting lms access token with parameters %s" % token_params)
    # get the pem-encoded content
    private_key = get_pem_text_from_file(private_key_path)

    headers = get_headers_to_jwt_encode(private_key)

    token = jwt.encode(token_params, private_key, algorithm="RS256", headers=headers)
    logger.debug("Obtaining token %s" % token)
    scope = scope or " ".join(
        [
            "https://purl.imsglobal.org/spec/lti-ags/scope/score",
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
            "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
        ]
    )
    logger.debug("Scope is %s" % scope)
    params = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": token.decode(),
        "scope": scope,
    }
    logger.debug("OAuth parameters are %s" % params)
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


def get_headers_to_jwt_encode(private_key_text: str) -> dict:
    """
    Helper method that gets the dict headers to use in jwt.encode method

    Args:
        private_key_text: The PEM-Encoded content as text

    Returns: A dict if the publickey can be exported or None otherwise
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
    """
    # check the pem permission
    if not os.access(private_key_path, os.R_OK):
        raise PermissionError()
    # parse file generates a list of PEM objects
    certs = pem.parse_file(private_key_path)
    if not certs:
        raise Exception("Invalid pem file.")

    return certs[0].as_text()


class LTI13Authenticator(OAuthenticator):
    """
    JupyterHub LTI 1.3 Authenticator which extends the `OAuthenticator` class. (LTI 1.3
    is basically an extension of OIDC/OAuth2). Messages sent to this authenticator are sent
    from a platform, such as an LMS. JupyterHub, as the authenticator, works as the External Tool.

    This class utilizes the following configurables defined in the `OAuthenticator` base class
    (all are required unless stated otherwise):

        - authorize_url
        - oauth_callback_url
        - token_url
        - userdata_url
        - (Optional) client_id

    Ref:
      - https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/oauth2.py
      - http://www.imsglobal.org/spec/lti/v1p3/
    """

    login_service = "LTI 1.3"

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    # The client_id, authorize_url, and token_url config settings
    # are available in the OAuthenticator base class. They are overriden
    # with this class for the sake of clarity. The endpoint config is specific
    # to LTI 1.3.
    client_id = Unicode(
        "",
        help="""
        The LTI 1.3 client id that identifies the tool installation with the
        platform.
        """,
    ).tag(config=True)

    endpoint = Unicode(
        os.getenv("LTI13_ENDPOINT", ""),
        config=True,
        help="""
        The platform's base endpoint used when redirecting requests to the platform
        after receiving the initial login request.
        """,
    ).tag(config=True)

    oauth_callback_url = Unicode(
        os.getenv("LTI13_CALLBACK_URL", ""),
        config=True,
        help="""Callback URL to use.
        Should match the redirect_uri sent from the platform during the
        initial login request.""",
    ).tag(config=True)

    username_key = Unicode(
        "email",
        allow_none=False,
        config=True,
        help="""
        JWT claim present in LTI 1.3 login initiation flow used to set the user's JupyterHub's username.
        Some common examples include:

          - User's email address: email
          - Given name: given_name
        
        Your LMS (Canvas / Open EdX / Moodle / others) may provide additional keys in the
        LTI 1.3 login initiatino flow that you can use to set the username. In most cases these
        are located in the `https://purl.imsglobal.org/spec/lti/claim/custom` claim. You may also
        have the option of using variable substitutions to fetch values that aren't provided with
        your vendor's standard LTI 1.3 login initiation flow request. If your platform's LTI 1.3
        settings are defined with privacy enabled, then by default the `sub` claim is used to set the
        username.

        Reference the IMS LTI specification on variable substitutions:
        http://www.imsglobal.org/spec/lti/v1p3/#customproperty.
        """,
    )

    async def authenticate(  # noqa: C901
        self, handler: LTI13LoginHandler, data: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Overrides authenticate from base class to handle LTI 1.3 authentication requests.

        Args:
          handler: handler object
          data: authentication dictionary

        Returns:
          Authentication dictionary
        """
        validator = LTI13LaunchValidator()

        # get jwks endpoint and token to use as args to decode jwt.
        self.log.debug("JWKS platform endpoint is %s" % self.endpoint)
        id_token = handler.get_argument("id_token")
        self.log.debug("ID token issued by platform is %s" % id_token)

        # extract claims from jwt (id_token) sent by the platform. as tool use the jwks (public key)
        # to verify the jwt's signature.
        jwt_decoded = await validator.jwt_verify_and_decode(
            id_token, self.endpoint, False, audience=self.client_id
        )
        self.log.debug("Decoded JWT: %s" % jwt_decoded)

        if validator.validate_launch_request(jwt_decoded):
            # get the username_key. if empty or None, fetch the username from the request's lms_user_id value.
            # if the lms_user_id isn't available raise an 400 http error.
            username = jwt_decoded.get(self.username_key)
            if not username:
                # if the username isn't set, fallback to fetch the username from the
                # subject claim
                if "sub" in jwt_decoded and jwt_decoded["sub"]:
                    username = jwt_decoded["sub"]
                else:
                    raise HTTPError(400, "Unable to set the username")

            self.log.debug("username is %s" % username)

            return {
                "name": username,
                "auth_state": {k: v for k, v in jwt_decoded.items()},  # noqa: E231
            }


class LocalLTI13Authenticator(LocalAuthenticator, OAuthenticator):

    """A version that mixes in local system user creation"""

    pass
