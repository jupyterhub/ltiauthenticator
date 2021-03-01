import json
import jwt

from josepy.jws import JWS
from josepy.jws import Header

from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError

from traitlets.config import LoggingConfigurable

from typing import Any
from typing import Dict

from ltiauthenticator.lti13.constants import LTI13_DEEP_LINKING_REQUIRED_CLAIMS
from ltiauthenticator.lti13.constants import LTI13_GENERAL_REQUIRED_CLAIMS
from ltiauthenticator.lti13.constants import LTI13_RESOURCE_LINK_REQUIRED_CLAIMS
from ltiauthenticator.lti13.constants import LTI13_LOGIN_REQUEST_ARGS
from ltiauthenticator.lti13.constants import LTI13_RESOURCE_LINK_REQUIRED_CLAIMS
from ltiauthenticator.lti13.constants import LTI13_DEEP_LINKING_REQUIRED_CLAIMS


class LTI13LaunchValidator(LoggingConfigurable):
    """
    Allows JupyterHub to verify LTI 1.3 compatible requests as a tool (known as a tool
    provider with LTI 1.1).
    """

    async def _retrieve_matching_jwk(
        self, endpoint: str, header_kid: str, verify: bool = True
    ) -> Any:
        """
        Retrieves the matching cryptographic key from the platform as a
        JSON Web Key (JWK).

        Args:
          endpoint: platform jwks endpoint
          header_kid: the kid received within the id_token
          verify: if true, validate certificate

        Returns:
          JSON web key
        """
        client = AsyncHTTPClient()
        resp = await client.fetch(endpoint, validate_cert=verify)
        platform_jwks = json.loads(resp.body)
        self.log.debug("Retrieved jwks from lms platform %s" % platform_jwks)

        if not platform_jwks or "keys" not in platform_jwks:
            raise ValueError("Platform endpoint returned an empty jwks")

        key = None
        for jwk in platform_jwks["keys"]:
            if jwk["kid"] != header_kid:
                continue
            key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            self.log.debug("Get keys from jwks dict  %s" % key)
        if key is None:
            error_msg = (
                f"No matching keys were found in the platform. kid: {header_kid}"
            )
            self.log.debug(error_msg)
            raise ValueError(error_msg)

        return key

    def _validate_global_required_keys(
        self,
        jwt_decoded: Dict[str, Any],
    ) -> bool:
        """Validates required LTI 1.3 keys (claims)

        Args:
            jwt_decoded (Dict[str, Any]): decoded JSON Web Token from the request.

        Raises:
            HTTPError: if the required claims is not included or if it has the wrong value

        Returns:
            True if the request is correct
        """
        # does all the required keys exist?
        for claim, v in LTI13_GENERAL_REQUIRED_CLAIMS.items():
            if claim not in jwt_decoded:
                raise HTTPError(
                    400, "Required claim %s not included in request" % claim
                )
        # some fixed values
        lti_version = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/version"
        )
        if lti_version != "1.3.0":
            raise HTTPError(400, "Incorrect value %s for version claim" % lti_version)

        # validate context label
        context_claim = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/context", None
        )
        context_label = (
            jwt_decoded.get("https://purl.imsglobal.org/spec/lti/claim/context").get(
                "label"
            )
            if context_claim
            else None
        )
        if context_label == "":
            raise HTTPError(
                400,
                "Missing course context label for claim https://purl.imsglobal.org/spec/lti/claim/context",
            )
        # validate message type value
        message_type = jwt_decoded.get(
            "https://purl.imsglobal.org/spec/lti/claim/message_type", None
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
            raise HTTPError(400, "Incorrect value %s for version claim" % message_type)

        return True

    async def jwt_verify_and_decode(
        self,
        id_token: str,
        jwks_endpoint: str,
        verify: bool = True,
        audience: str = None,
    ) -> Dict[str, str]:
        """
        Decodes the JSON Web Token (JWT) sent from the platform. The JWT should contain claims
        that represent properties associated with the request. This method implicitly verifies the JWT's
        signature using the platform's public key.

        Args:
          id_token: JWT token issued by the platform
          jwks_endpoint: JSON web key (publick key) endpoint
          verify: verify whether or not to verify JWT when decoding. Defaults to True.
          audience: the platform's OAuth2 Audience (aud). This value usually coincides with the
            token endpoint for the platform (LMS) such as https://my.lms.domain/login/oauth2/token

        Returns:
          Decoded dictionary that represents the k/v's included with the JWT
        """
        if verify is False:
            self.log.debug(
                "JWK verification is off, returning token %s"
                % jwt.decode(id_token, verify=False)
            )
            return jwt.decode(id_token, verify=False)

        jws = JWS.from_compact(id_token)
        self.log.debug("Retrieving matching jws %s" % jws)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)
        self.log.debug("Header from decoded jwt %s" % header)

        key_from_jwks = await self._retrieve_matching_jwk(
            jwks_endpoint, verify, header.kid
        )
        self.log.debug(
            "Returning decoded jwt with token %s key %s and verify %s"
            % (id_token, key_from_jwks, verify)
        )

        return jwt.decode(id_token, key=key_from_jwks, verify=False, audience=audience)

    def is_deep_link_launch(
        self,
        jwt_decoded: Dict[str, Any],
    ) -> bool:
        """
        Returns whether or not the current launch is a deep linking launch.

        Args:
          jwt_decoded: decoded JWT

        Returns:
          True if the current launch is a deep linking launch.
        """
        return (
            jwt_decoded.get(
                "https://purl.imsglobal.org/spec/lti/claim/message_type", None
            )
            == "LtiDeepLinkingRequest"
        )

    def validate_launch_request(
        self,
        jwt_decoded: Dict[str, Any],
    ) -> bool:
        """
        Validates that a given LTI 1.3 launch request has the required required claims The
        required claims combine the required claims according to the LTI 1.3 standard and the
        required claims for this setup to work properly, which are obtaind from the LTI 1.3 standard
        optional claims and LIS optional claims.

        The required claims are defined as constants.

        Args:
          jwt_decoded: decode JWT payload

        Returns:
          True if the validation passes, False otherwise.

        Raises:
          HTTPError if a required claim is not included in the dictionary or if the message_type and/or
          version claims do not have the correct value.
        """
        # first validate global required keys
        if self._validate_global_required_keys(jwt_decoded):
            # get the message type for additional validations
            is_deep_linking = self.is_deep_link_launch(jwt_decoded)
            required_claims_by_message_type = (
                LTI13_DEEP_LINKING_REQUIRED_CLAIMS
                if is_deep_linking
                else LTI13_RESOURCE_LINK_REQUIRED_CLAIMS
            )

            for claim, v in required_claims_by_message_type.items():
                if claim not in jwt_decoded:
                    raise HTTPError(
                        400, "Required claim %s not included in request" % claim
                    )
            if not is_deep_linking:
                # custom validations with resource launch
                if (
                    jwt_decoded.get(
                        "https://purl.imsglobal.org/spec/lti/claim/resource_link"
                    ).get("id")
                    == ""
                ):
                    raise HTTPError(
                        400,
                        "Incorrect value %s for id in resource_link claim"
                        % jwt_decoded.get(
                            "https://purl.imsglobal.org/spec/lti/claim/resource_link"
                        ).get("id"),
                    )

        return True

    def validate_login_request(self, args: Dict[str, Any]) -> bool:
        """
        Validates step 1 of authentication request.

        Args:
          args: dictionary that represents keys/values sent in authentication request

        Returns:
          True if the validation is ok, false otherwise
        """
        for param in LTI13_LOGIN_REQUEST_ARGS:
            if param not in args:
                raise HTTPError(
                    400, "Required LTI 1.3 arg %s not included in request" % param
                )
            if not args.get(param):
                raise HTTPError(
                    400, "Required LTI 1.3 arg %s does not have a value" % param
                )
        return True
