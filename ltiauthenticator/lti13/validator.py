from typing import Any, Dict, List

import jwt
from traitlets.config import LoggingConfigurable

from ltiauthenticator.lti13.constants import (
    LTI13_AUTH_RESPONSE_ARGS,
    LTI13_DEEP_LINKING_REQUIRED_CLAIMS,
    LTI13_GENERAL_REQUIRED_CLAIMS,
    LTI13_INIT_LOGIN_REQUEST_ARGS,
    LTI13_RESOURCE_LINK_REQUEST_REQUIRED_CLAIMS,
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
          MissingRequiredArgumentError if an argument is missing
        """
        self._validate_required_args(args, LTI13_INIT_LOGIN_REQUEST_ARGS)

    def validate_auth_response(self, args: Dict[str, Any]) -> None:
        """
        Validate the reponse from the authorization server and ensures that the required
        parameters are present.

        Args:
          args: dictionary that represents keys/values sent in authentication response

        Raises:
          MissingRequiredArgumentError if an required argument is missing or has no value
        """
        self._validate_required_args(args, LTI13_AUTH_RESPONSE_ARGS)

    def _validate_required_args(self, args: Dict[str, Any], required: List[str]):
        for a in required:
            if a not in args:
                raise MissingRequiredArgumentError(
                    f"Required LTI 1.3 arg {a} not in request"
                )
            if not args.get(a):
                raise MissingRequiredArgumentError(
                    f"Required LTI 1.3 arg {a} needs a value"
                )

    def verify_and_decode_jwt(
        self, encoded_jwt, issuer, audience, jwks_endpoint, jwks_algorithms, **kwargs
    ):
        """
        Verify the JWT against the public keys provided in a JSON Web Key Set
        endpoint provided by the platform, and then return the payload in the
        jwt.
        """
        if not issuer:
            self.log.warning("No issuer identifyer configured")

        # reject unsigned id_token if encription is negotiated
        verification_options = kwargs.pop("options", {})
        verification_options["verify_signature"] = (
            verification_options.get("verify_signature", True) or jwks_endpoint != ""
        )

        try:
            if verification_options["verify_signature"]:
                jwks_client = jwt.PyJWKClient(jwks_endpoint)
                signing_key = jwks_client.get_signing_key_from_jwt(encoded_jwt)
                key = signing_key.key
            else:
                key = ""

            id_token = jwt.decode(
                encoded_jwt,
                key,
                algorithms=jwks_algorithms,
                audience=audience,
                issuer=issuer,
                options=verification_options,
                **kwargs,
            )
        except jwt.PyJWTError as e:
            raise TokenError(str(e))

        return id_token

    def _check_general_required_keys(self, id_token: Dict[str, Any]) -> None:
        """Validates required LTI 1.3 claims (keys in jwt_decoded)

        Args:
            jwt_decoded: decoded JWT payload

        Raises:
            HTTPError: if the required claims is not included or if it has the
            wrong value
        """
        # does all the required keys exist?
        for k in LTI13_GENERAL_REQUIRED_CLAIMS:
            if k not in id_token:
                raise MissingRequiredArgumentError(
                    f"Required claim {k} not included in request"
                )

        lti_version = id_token.get("https://purl.imsglobal.org/spec/lti/claim/version")
        if lti_version != "1.3.0":
            raise IncorrectValueError(
                f"Incorrect value {lti_version} for version claim"
            )

        # validate context label
        context_claim = id_token.get(
            "https://purl.imsglobal.org/spec/lti/claim/context"
        )
        context_label = context_claim.get("label") if context_claim else None
        if context_label == "":
            raise MissingRequiredArgumentError(
                "Claim https://purl.imsglobal.org/spec/lti/claim/context present, but context label is missing."
            )

        # validate message type value
        message_type = id_token.get(
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        )
        if (
            message_type
            != LTI13_RESOURCE_LINK_REQUEST_REQUIRED_CLAIMS[
                "https://purl.imsglobal.org/spec/lti/claim/message_type"
            ]
            and message_type
            != LTI13_DEEP_LINKING_REQUIRED_CLAIMS[
                "https://purl.imsglobal.org/spec/lti/claim/message_type"
            ]
        ):
            raise IncorrectValueError(
                f"Incorrect value {message_type} for message_type claim"
            )

    def validate_id_token(self, id_token: Dict[str, Any]) -> None:
        """
        Validates that a LTI 1.3 launch request's decoded JWT has required
        claims (dictionary keys of id_token).

        The required claims are defined by the LTI 1.3 standard, see
        https://www.imsglobal.org/spec/lti/v1p3#required-message-claims.

        Args:
          id_token: decoded JWT payload of a launch request

        Raises:
          HTTPError if a required claim is not included in the dictionary or if
          the message_type and/or version claims do not have the correct value.
        """
        self._check_general_required_keys(id_token)

        # message_type influences what claims are required
        message_type = id_token[
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        ]
        is_deep_linking = message_type == "LtiDeepLinkingRequest"
        if is_deep_linking:
            required_claims = LTI13_DEEP_LINKING_REQUIRED_CLAIMS
        else:
            required_claims = LTI13_RESOURCE_LINK_REQUEST_REQUIRED_CLAIMS

        for k, _ in required_claims.items():
            if k not in id_token:
                raise MissingRequiredArgumentError(
                    f"Required claim {k} not included in request"
                )

        # custom validations with resource launch
        if not is_deep_linking:
            id = id_token.get(
                "https://purl.imsglobal.org/spec/lti/claim/resource_link"
            ).get("id")
            if not id:
                raise MissingRequiredArgumentError(
                    "resource_link claim's id can't be empty"
                )


class ValidationError(Exception):
    """Base class for validation exceptions."""


class MissingRequiredArgumentError(ValidationError):
    """Exception raised for missing required request arguments."""

    pass


class IncorrectValueError(ValidationError):
    """Exception raised for incorrect values."""

    pass


class TokenError(ValidationError):
    """Exception raised for failed JWT decoding or verification."""

    pass
