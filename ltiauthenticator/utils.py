import logging
import os
from typing import Any, Dict, List

from tornado.web import RequestHandler

from .lti13.constants import (
    DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR,
    DEFAULT_ROLE_NAMES_FOR_STUDENT,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def user_is_a_student(user_role: str) -> str:
    """Determins if the user has a Student/Learner role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case student string
    """
    if not user_role:
        raise ValueError("user_role must have a value")
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_STUDENT


def user_is_an_instructor(user_role: str) -> str:
    """Determins if the user has a Instructor/Teacher role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case instructor string
    """
    if not user_role:
        raise ValueError("user_role must have a value")
    # find the extra role names to recognize an instructor (to be added in the grader group)
    extra_roles = os.environ.get("EXTRA_ROLE_NAMES_FOR_INSTRUCTOR") or []
    if extra_roles:
        extra_roles = extra_roles.lower().split(",")
        DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR.extend(extra_roles)
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR
