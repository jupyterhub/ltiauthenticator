from typing import Any, Dict

import jwt
from tornado.web import HTTPError
from traitlets.config import LoggingConfigurable

from ltiauthenticator.lti13.constants import (
    LTI13_DEEP_LINKING_REQUIRED_CLAIMS,
    LTI13_GENERAL_REQUIRED_CLAIMS,
    LTI13_LOGIN_REQUEST_ARGS,
    LTI13_RESOURCE_LINK_REQUIRED_CLAIMS,
)


class LTI13LaunchValidator(LoggingConfigurable):
    """
    Allows JupyterHub to verify LTI 1.3 compatible requests as a tool (known as a tool
    provider with LTI 1.1).
    """

    def validate_login_request(self, args: Dict[str, Any]) -> None:
        """
        Validates the initial authentication request and ensures the required
        claims are included in said request.

        Args:
          args: dictionary that represents keys/values sent in authentication request

        Raises:
          HTTPError if validation fails.
        """
        for a in LTI13_LOGIN_REQUEST_ARGS:
            if a not in args:
                raise HTTPError(400, f"Required LTI 1.3 arg {a} not in request")
            if not args.get(a):
                raise HTTPError(400, f"Required LTI 1.3 arg {a} needs a value")

    def verify_and_decode_jwt(
        self, encoded_jwt, audience, jwks_endpoint, jwks_algorithms, **kwargs
    ):
        """
        Verify the JWT against the public keys provided in a JSON Web Key Set
        endpoint provided by the platform, and then return the payload in the
        jwt.
        """
        jwks_client = jwt.PyJWKClient(jwks_endpoint)
        signing_key = jwks_client.get_signing_key_from_jwt(encoded_jwt)
        jwt_decoded = jwt.decode(
            encoded_jwt,
            signing_key.key,
            algorithms=jwks_algorithms,
            audience=audience,
            **kwargs,
        )
        return jwt_decoded

    def _check_general_required_keys(self, jwt_decoded: Dict[str, Any]) -> None:
        """Validates required LTI 1.3 claims (keys in jwt_decoded)

        Args:
            jwt_decoded: decoded JWT payload

        Raises:
            HTTPError: if the required claims is not included or if it has the
            wrong value
        """
        # does all the required keys exist?
        for k, v in LTI13_GENERAL_REQUIRED_CLAIMS.items():
            if k not in jwt_decoded:
                raise HTTPError(400, f"Required claim {k} not included in request")

        lti_version = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/version"
        )
        if lti_version != "1.3.0":
            raise HTTPError(400, f"Incorrect value {lti_version} for version claim")

        # validate context label
        context_claim = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/context"
        )
        context_label = context_claim.get("label") if context_claim else None
        if context_label == "":
            raise HTTPError(
                400,
                "Missing course context label for claim https://purl.imsglobal.org/spec/lti/claim/context",
            )

        # validate message type value
        message_type = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        )
        if (
            message_type
            != LTI13_RESOURCE_LINK_REQUIRED_CLAIMS[
                "https://purl.imsglobal.org/spec/lti/claim/message_type"
            ]
            and message_type
            != LTI13_DEEP_LINKING_REQUIRED_CLAIMS[
                "https://purl.imsglobal.org/spec/lti/claim/message_type"
            ]
        ):
            raise HTTPError(
                400, f"Incorrect value {message_type} for message_type claim"
            )

    def validate_launch_request(self, jwt_decoded: Dict[str, Any]) -> None:
        """
        Validates that a LTI 1.3 launch request's decoded JWT has required
        claims (dictionary keys of jwt_decoded).

        The required claims are defined by the LTI 1.3 standard, see
        https://www.imsglobal.org/spec/lti/v1p3#required-message-claims.

        Args:
          jwt_decoded: decoded JWT payload

        Raises:
          HTTPError if a required claim is not included in the dictionary or if
          the message_type and/or version claims do not have the correct value.
        """
        self._check_general_required_keys(jwt_decoded)

        # message_type influences what claims are required
        message_type = jwt_decoded[
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        ]
        is_deep_linking = message_type == "LtiDeepLinkingRequest"
        if is_deep_linking:
            required_claims = LTI13_DEEP_LINKING_REQUIRED_CLAIMS
        else:
            required_claims = LTI13_RESOURCE_LINK_REQUIRED_CLAIMS

        for k, _ in required_claims.items():
            if k not in jwt_decoded:
                raise HTTPError(400, f"Required claim {k} not included in request")

        # custom validations with resource launch
        if not is_deep_linking:
            id = jwt_decoded.get(
                "https://purl.imsglobal.org/spec/lti/claim/resource_link"
            ).get("id")
            if not id:
                raise HTTPError(400, "resource_link claim's id can't be empty")
