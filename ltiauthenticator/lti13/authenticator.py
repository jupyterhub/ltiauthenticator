from oauthenticator.oauth2 import OAuthenticator

from tornado.web import HTTPError

from typing import Dict

from jupyterhub.auth import LocalAuthenticator

from ltiauthenticator.lti13.handlers import LTI13LoginHandler
from ltiauthenticator.lti13.handlers import LTI13CallbackHandler
from ltiauthenticator.lti13.validator import LTI13LaunchValidator
from ltiauthenticator.lti13.utils import normalize_string
from ltiauthenticator.lti13.utils import email_to_username
from ltiauthenticator.lti13.utils import normalize_string
from ltiauthenticator.lti13.utils import normalize_string


class LTI13Authenticator(OAuthenticator):
    """Custom authenticator used with LTI 1.3 requests"""

    login_service = "LTI13Authenticator"

    # handlers used for login, callback, and jwks endpoints
    login_handler = LTI13LoginHandler
    callback_handler = LTI13CallbackHandler

    async def authenticate(  # noqa: C901
        self, handler: LTI13LoginHandler, data: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Overrides authenticate from base class to handle LTI 1.3 authentication requests. This class
        utilizes the following configurables defined in the OAuthenticator base class (all are required
        unless stated otherwise):

        - authorize_url
        - oauth_callback_url
        - token_url
        - userdata_url
        - (Optional) client_id

        Ref: https://github.com/jupyterhub/oauthenticator/blob/master/oauthenticator/oauth2.py

        Args:
          handler: handler object
          data: authentication dictionary

        Returns:
          Authentication dictionary
        """
        validator = LTI13LaunchValidator()

        # get jwks endpoint and token to use as args to decode jwt. we could pass in
        # self.endpoint directly as arg to jwt_verify_and_decode() but logging the
        self.log.debug("JWKS platform endpoint is %s" % self.endpoint)
        id_token = handler.get_argument("id_token")
        self.log.debug("ID token issued by platform is %s" % id_token)

        # extract claims from jwt (id_token) sent by the platform. as tool use the jwks (public key)
        # to verify the jwt's signature.
        jwt_decoded = await validator.jwt_verify_and_decode(
            id_token, self.endpoint, False, audience=self.client_id
        )
        self.log.debug("Decoded JWT is %s" % jwt_decoded)

        if validator.validate_launch_request(jwt_decoded):
            course_id = jwt_decoded[
                "https://purl.imsglobal.org/spec/lti/claim/context"
            ]["label"]
            course_id = normalize_string(course_id)
            self.log.debug("Normalized course label is %s" % course_id)
            username = ""
            if "email" in jwt_decoded and jwt_decoded["email"]:
                username = email_to_username(jwt_decoded["email"])
            elif "name" in jwt_decoded and jwt_decoded["name"]:
                username = jwt_decoded["name"]
            elif "given_name" in jwt_decoded and jwt_decoded["given_name"]:
                username = jwt_decoded["given_name"]
            elif "family_name" in jwt_decoded and jwt_decoded["family_name"]:
                username = jwt_decoded["family_name"]
            elif (
                "https://purl.imsglobal.org/spec/lti/claim/lis" in jwt_decoded
                and "person_sourcedid"
                in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"]
                and jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"][
                    "person_sourcedid"
                ]
            ):
                username = jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/lis"][
                    "person_sourcedid"
                ].lower()
            elif (
                "lms_user_id"
                in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"]
                and jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"][
                    "lms_user_id"
                ]
            ):
                username = str(
                    jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/custom"][
                        "lms_user_id"
                    ]
                )
            self.log.debug("username is %s" % username)
            # ensure the username is normalized
            self.log.debug("username is %s" % username)
            if username == "":
                raise HTTPError("Unable to set the username")

            # set role to learner role (by default) if instructor or learner/student roles aren't
            # sent with the request
            user_role = "Learner"
            for role in jwt_decoded["https://purl.imsglobal.org/spec/lti/claim/roles"]:
                if role.find("Instructor") >= 1:
                    user_role = "Instructor"
                elif role.find("Learner") >= 1 or role.find("Student") >= 1:
                    user_role = "Learner"
            self.log.debug("user_role is %s" % user_role)

            launch_return_url = ""
            if (
                "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                in jwt_decoded
                and "return_url"
                in jwt_decoded[
                    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                ]
            ):
                launch_return_url = jwt_decoded[
                    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
                ]["return_url"]

            lms_user_id = jwt_decoded["sub"] if "sub" in jwt_decoded else username

            # ensure the user name is normalized
            username_normalized = normalize_string(username)
            self.log.debug("Assigned username is: %s" % username_normalized)

            return {
                "name": username_normalized,
                "auth_state": {
                    "course_id": course_id,
                    "user_role": user_role,
                    "lms_user_id": lms_user_id,
                    "launch_return_url": launch_return_url,
                },  # noqa: E231
            }


class LocalLTI13Authenticator(LocalAuthenticator, OAuthenticator):

    """A version that mixes in local system user creation"""

    pass
