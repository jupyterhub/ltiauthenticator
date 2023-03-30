"""All custom exceptions defined in one place."""


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


class InvalidAudienceError(ValidationError):
    """Exception raised for invalid audience."""

    pass


class LoginError(Exception):
    """Lookup of username in ID token failed"""

    pass
