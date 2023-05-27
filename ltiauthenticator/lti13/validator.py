from calendar import timegm
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import jwt
from traitlets import Int
from traitlets.config import LoggingConfigurable

from .constants import (
    LTI13_AUTH_RESPONSE_ARGS,
    LTI13_DEEP_LINKING_REQUIRED_CLAIMS,
    LTI13_GENERAL_REQUIRED_CLAIMS,
    LTI13_INIT_LOGIN_REQUEST_ARGS,
    LTI13_RESOURCE_LINK_REQUEST_REQUIRED_CLAIMS,
)
from .error import (
    IncorrectValueError,
    InvalidAudienceError,
    MissingRequiredArgumentError,
    TokenError,
)


def now() -> int:
    return timegm(datetime.now(tz=timezone.utc).utctimetuple())


class LTI13LaunchValidator(LoggingConfigurable):
    """
    Allows JupyterHub to verify LTI 1.3 compatible requests as a tool (known as a tool
    provider with LTI 1.1).
    """

    time_leeway = Int(
        0,
        config=True,
        help="""
        A time margin in seconds for the JWT expiration checks.

        It will be added as a grace period to mitigate clock drift issues.
        """,
    )

    max_age = Int(
        600,
        config=True,
        help="""
        Maximum age of an id_token to be accepted.
        """,
    )

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

    def _check_arg_not_missing(self, args: Dict[str, Any], required: Iterable[str]):
        for a in required:
            if a not in args:
                raise MissingRequiredArgumentError(
                    f"Required LTI 1.3 arg {a} not in request"
                )

    def _check_arg_not_empty(self, args: Dict[str, Any], required: Iterable[str]):
        for a in required:
            if not args.get(a):
                raise MissingRequiredArgumentError(
                    f"Required LTI 1.3 arg {a} needs a value"
                )

    def _validate_required_args(self, args: Dict[str, Any], required: Iterable[str]):
        self._check_arg_not_missing(args, required)
        self._check_arg_not_empty(args, required)

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
                leeway=self.time_leeway,
                **kwargs,
            )
        except jwt.InvalidAudienceError as e:
            raise InvalidAudienceError(str(e))
        except jwt.PyJWTError as e:
            raise TokenError(str(e))

        return id_token

    def _check_message_type(self, id_token: Dict[str, Any]) -> None:
        """Validate message type value"""
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

    def _check_context_label(self, id_token: Dict[str, Any]) -> None:
        """Validate context label."""
        context_claim = id_token.get(
            "https://purl.imsglobal.org/spec/lti/claim/context"
        )
        context_label = context_claim.get("label") if context_claim else None
        if context_label == "":
            raise MissingRequiredArgumentError(
                "Claim https://purl.imsglobal.org/spec/lti/claim/context present, but context label is missing."
            )

    def _check_lti_version(self, id_token: Dict[str, Any]) -> None:
        """Check version claim."""
        lti_version = id_token.get("https://purl.imsglobal.org/spec/lti/claim/version")
        if lti_version != "1.3.0":
            raise IncorrectValueError(
                f"Incorrect value {lti_version} for version claim"
            )

    def _check_resource_link_id(self, id_token: Dict[str, Any]) -> None:
        """Check if resource_link claim has id set."""
        id = id_token.get(
            "https://purl.imsglobal.org/spec/lti/claim/resource_link", {}
        ).get("id")
        if not id:
            raise MissingRequiredArgumentError(
                "resource_link claim's id can't be empty"
            )

    def validate_azp_claim(
        self, id_token: Dict[str, Any], client_id: Iterable[str]
    ) -> None:
        """Check if azp claim is present and matches client_id."""
        aud = id_token["aud"]
        need_azp = isinstance(id_token["aud"], list) and len(aud) > 1
        if not need_azp:
            return
        azp = id_token.get("azp")
        if not azp:
            raise MissingRequiredArgumentError(
                "azp claim is missing although multiple values for aud are given."
            )
        if azp not in client_id:
            raise InvalidAudienceError("azp claim does not match client_id.")

    def _check_if_iat_is_too_old(self, id_token: Dict[str, Any]) -> None:
        """Raise TokenError if iat is too old."""
        iat = id_token["iat"]
        if iat < now() - self.max_age - self.time_leeway:
            raise TokenError("id_token issued too long ago.")

    def validate_id_token(self, id_token: Dict[str, Any]) -> None:
        """
        Validates that a LTI 1.3 launch request's decoded JWT has required
        claims (dictionary keys of id_token).

        The required claims are defined by the LTI 1.3 standard, see
        https://www.imsglobal.org/spec/lti/v1p3#required-message-claims.

        Args:
          id_token: decoded JWT payload of a launch request

        Raises:
          Subclass of ValidationError.
        """
        self._check_arg_not_missing(id_token, LTI13_GENERAL_REQUIRED_CLAIMS.keys())
        self._check_lti_version(id_token)
        self._check_context_label(id_token)
        self._check_message_type(id_token)
        self._check_if_iat_is_too_old(id_token)

        # message_type influences what claims are required
        message_type = id_token[
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        ]
        is_deep_linking = message_type == "LtiDeepLinkingRequest"

        if is_deep_linking:
            self._check_arg_not_missing(
                id_token, LTI13_DEEP_LINKING_REQUIRED_CLAIMS.keys()
            )
        else:
            self._check_arg_not_missing(
                id_token, LTI13_RESOURCE_LINK_REQUEST_REQUIRED_CLAIMS.keys()
            )
            self._check_resource_link_id(id_token)
