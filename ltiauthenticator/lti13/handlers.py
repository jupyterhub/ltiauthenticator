import logging
import hashlib
import json
import os
import pem
import re

from Crypto.PublicKey import RSA

from jupyterhub.handlers import BaseHandler

from oauthenticator.oauth2 import STATE_COOKIE_NAME
from oauthenticator.oauth2 import _serialize_state
from oauthenticator.oauth2 import guess_callback_uri
from oauthenticator.oauth2 import OAuthLoginHandler
from oauthenticator.oauth2 import OAuthCallbackHandler

from tornado.httputil import url_concat
from tornado.web import HTTPError
from tornado.web import RequestHandler

from typing import cast
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse
import uuid

from ltiauthenticator.lti13.validator import LTI13LaunchValidator
from ltiauthenticator.lti13.utils import get_jwk
from ltiauthenticator.lti13.utils import convert_request_to_dict
from ltiauthenticator.lti13.utils import get_client_protocol


logger = logging.getLogger(__name__)


class LTI13LoginHandler(OAuthLoginHandler):
    """
    Handles JupyterHub authentication requests according to the
    LTI 1.3 standard.
    """

    def authorize_redirect(
        self,
        client_id: str = None,
        login_hint: str = None,
        lti_message_hint: str = None,
        nonce: str = None,
        redirect_uri: str = None,
        state: str = None,
    ) -> None:
        """
        Overrides the OAuth2Mixin.authorize_redirect method to to initiate the LTI 1.3 / OIDC
        login flow. Arguments are redirected to the platform's authorization url for further
        processing.

        References:
        https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        http://www.imsglobal.org/spec/lti/v1p3/#additional-login-parameters-0

        Args:
          client_id: used to identify the tool's installation with a platform
          redirect_uri: redirect url specified during tool installation (callback url)
          login_hint: opaque value used by the platform for user identity
          lti_message_hint: signed JWT which contains information needed to perform the
            launch including issuer, user and context information
          nonce: unique value sent to allow recipients to protect themselves against replay attacks
          state: opaque value for the platform to maintain state between the request and
            callback and provide Cross-Site Request Forgery (CSRF) mitigation.
        """
        handler = cast(RequestHandler, self)
        args = {"response_type": "id_token"}
        args["scope"] = "openid"
        if redirect_uri is not None:
            args["redirect_uri"] = redirect_uri
        if client_id is not None:
            args["client_id"] = client_id
        extra_params = {"extra_params": {}}
        extra_params["response_mode"] = "form_post"
        extra_params["prompt"] = "none"
        if login_hint is not None:
            extra_params["login_hint"] = login_hint
        if lti_message_hint is not None:
            extra_params["lti_message_hint"] = lti_message_hint
        if state is not None:
            extra_params["state"] = state
        if nonce is not None:
            extra_params["nonce"] = nonce
        args.update(extra_params)
        url = os.environ.get("LTI13_AUTHORIZE_URL")
        if not url:
            raise EnvironmentError("LTI13_AUTHORIZE_URL env var is not set")
        handler.redirect(url_concat(url, args))

    def get_state(self):
        next_url = original_next_url = self.get_argument("next", None)
        if not next_url:
            # try with the target_link_uri arg
            target_link = self.get_argument("target_link_uri", "")
            if "next" in target_link:
                logger.debug(
                    f"Trying to get the next-url from target_link_uri: {target_link}"
                )
                next_search = re.search("next=(.*)", target_link, re.IGNORECASE)
                if next_search:
                    next_url = next_search.group(1)
                    # decode the some characters obtained with the link builder
                    next_url = unquote(next_url)
            elif not target_link.endswith("/hub"):
                next_url = target_link
        if next_url:
            # avoid browsers treating \ as /
            next_url = next_url.replace("\\", quote("\\"))
            # disallow hostname-having urls,
            # force absolute path redirect
            urlinfo = urlparse(next_url)
            next_url = urlinfo._replace(
                scheme="", netloc="", path="/" + urlinfo.path.lstrip("/")
            ).geturl()
            if next_url != original_next_url:
                logger.warning(
                    "Ignoring next_url %r, using %r", original_next_url, next_url
                )
        if self._state is None:
            self._state = _serialize_state(
                {"state_id": uuid.uuid4().hex, "next_url": next_url}
            )
        return self._state

    def set_state_cookie(self, state):
        """
        Overrides the base method to send the 'samesite' and 'secure' arguments and avoid the issues related with the use of iframes.
        It depends of python 3.8
        """
        self.set_secure_cookie(
            STATE_COOKIE_NAME,
            state,
            expires_days=1,
            httponly=True,
            samesite=None,
            secure=True,
        )

    def post(self):
        """
        Validates required login arguments sent from platform and then uses the authorize_redirect() method
        to redirect users to the authorization url.
        """
        validator = LTI13LaunchValidator()
        args = convert_request_to_dict(self.request.arguments)
        logger.debug("Initial login request args are %s" % args)
        if validator.validate_login_request(args):
            login_hint = args["login_hint"]
            logger.debug("login_hint is %s" % login_hint)
            lti_message_hint = args["lti_message_hint"]
            logger.debug("lti_message_hint is %s" % lti_message_hint)
            client_id = args["client_id"]
            logger.debug("client_id is %s" % client_id)
            redirect_uri = guess_callback_uri(
                "https", self.request.host, self.hub.server.base_url
            )
            logger.info("redirect_uri: %r", redirect_uri)
            state = self.get_state()
            self.set_state_cookie(state)
            nonce_raw = hashlib.sha256(state.encode())
            nonce = nonce_raw.hexdigest()
            self.authorize_redirect(
                client_id=client_id,
                login_hint=login_hint,
                lti_message_hint=lti_message_hint,
                nonce=nonce,
                redirect_uri=redirect_uri,
                state=state,
            )


class LTI13CallbackHandler(OAuthCallbackHandler):
    """
    LTI 1.3 call back handler
    """

    async def post(self):
        """
        Overrides the upstream get handler with it's standard implementation.
        """
        self.check_state()
        user = await self.login_user()
        logger.debug(f"user logged in: {user}")
        if user is None:
            raise HTTPError(403, "User missing or null")
        self.redirect(self.get_next_url(user))
        logger.debug("Redirecting user %s to %s" % (user.id, self.get_next_url(user)))


class LTI13ConfigHandler(BaseHandler):
    """
    Handles JSON configuration file for LTI 1.3
    """

    async def get(self) -> None:
        """
        Gets the JSON config which is used by LTI platforms
        to install the external tool.

        - The extensions key contains settings for specific vendors, such as canvas,
        moodle, edx, among others.
        - The tool uses public settings by default. Users that wish to install the tool with
        private settings should either copy/paste the json or toggle the application to private
        after it is installed with the platform.
        - Usernames are obtained by first attempting to get and normalize values sent when
        tools are installed with public settings. If private, the username is set using the
        anonumized user data when requests are sent with private installation settings.
        """
        self.set_header("Content-Type", "application/json")

        # get the origin protocol
        protocol = get_client_protocol(self)
        logger.debug("Origin protocol is: %s" % protocol)
        # build the full target link url value required for the jwks endpoint
        target_link_url = f"{protocol}://{self.request.host}/"
        logger.debug("Target link url is: %s" % target_link_url)
        keys = {
            "title": "LTIAuthenticator",
            "scopes": [
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/score",
                "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly",
                "https://canvas.instructure.com/lti/public_jwk/scope/update",
                "https://canvas.instructure.com/lti/data_services/scope/create",
                "https://canvas.instructure.com/lti/data_services/scope/show",
                "https://canvas.instructure.com/lti/data_services/scope/update",
                "https://canvas.instructure.com/lti/data_services/scope/list",
                "https://canvas.instructure.com/lti/data_services/scope/destroy",
                "https://canvas.instructure.com/lti/data_services/scope/list_event_types",
                "https://canvas.instructure.com/lti/feature_flags/scope/show",
                "https://canvas.instructure.com/lti/account_lookup/scope/show",
            ],
            "extensions": [
                {
                    "platform": "canvas.instructure.com",
                    "settings": {
                        "platform": "canvas.instructure.com",
                        "placements": [
                            {
                                "placement": "course_navigation",
                                "message_type": "LtiResourceLinkRequest",
                                "windowTarget": "_blank",
                                "target_link_uri": target_link_url,
                                "custom_fields": {
                                    "email": "$Person.email.primary",
                                    "lms_user_id": "$User.id",
                                },  # noqa: E231
                            },
                            {
                                "placement": "assignment_selection",
                                "message_type": "LtiResourceLinkRequest",
                                "target_link_uri": target_link_url,
                            },
                        ],
                    },
                    "privacy_level": "public",
                }
            ],
            "description": "JupyterHub Learning Tools Interoperability (LTI) v1.3 tool.",
            "custom_fields": {
                "email": "$Person.email.primary",
                "lms_user_id": "$User.id",
            },  # noqa: E231
            "public_jwk_url": f"{target_link_url}hub/lti13/jwks",
            "target_link_uri": target_link_url,
            "oidc_initiation_url": f"{target_link_url}hub/oauth_login",
        }
        self.write(json.dumps(keys))


class LTI13JWKSHandler(BaseHandler):
    """
    Handler to serve our JWKS
    """

    def get(self) -> None:
        """
        - This method requires that the LTI13_PRIVATE_KEY environment variable
        is set with the full path to the RSA private key in PEM format.
        """
        if not os.environ.get("LTI13_PRIVATE_KEY"):
            raise EnvironmentError("LTI13_PRIVATE_KEY environment variable not set")
        key_path = os.environ.get("LTI13_PRIVATE_KEY")
        # check the pem permission
        if not os.access(key_path, os.R_OK):
            logger.error(f"The pem file {key_path} cannot be load")
            raise PermissionError()
        private_key = pem.parse_file(key_path)
        public_key = RSA.import_key(private_key[0].as_text()).publickey().exportKey()
        logger.debug("public_key is %s" % public_key)

        jwk = get_jwk(public_key)
        logger.debug("the jwks is %s" % jwk)
        keys_obj = {"keys": []}
        keys_obj["keys"].append(jwk)
        # we do not need to use json.dumps because tornado is converting our dict automatically and adding the content-type as json
        # https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write
        self.write(keys_obj)
