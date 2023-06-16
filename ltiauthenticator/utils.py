import logging
import os
from typing import Any, Dict, List

from tornado.httputil import HTTPServerRequest

from .lti13.constants import (
    DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR,
    DEFAULT_ROLE_NAMES_FOR_STUDENT,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


try:
    from jupyterhub.utils import get_browser_protocol  # type: ignore

# if we are on jupyterhub < 2.0.2
except ImportError:

    def get_browser_protocol(request: HTTPServerRequest) -> str:
        """
        This is a copy of the jupyterhub-ltiauthenticator logic to get the first
        protocol value from the X-Scheme or X-Forwarded-Proto list, assuming there is more than
        one value. Otherwise, this returns the value as-is.

        Extracted as a method to facilitate testing.

        Args:
            handler: a tornado.web.RequestHandler object

        Returns:
            str of protocol seen by browser
        """
        proto_header = request.headers.get(
            "X-Scheme", request.headers.get("X-Forwarded-Proto", None)
        )
        if proto_header:
            hops = [h.strip() for h in proto_header.split(",")]
            return hops[0]

        return request.protocol


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


def user_is_a_student(user_role: str) -> bool:
    """Determins if the user has a Student/Learner role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case student string
    """
    if not user_role:
        raise ValueError("user_role must have a value")
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_STUDENT


def user_is_an_instructor(user_role: str) -> bool:
    """Determins if the user has a Instructor/Teacher role.

    Args:
        user_role: the user's rule

    Returns:
        Lower case instructor string
    """
    if not user_role:
        raise ValueError("user_role must have a value")
    # find the extra role names to recognize an instructor (to be added in the grader group)
    extra_roles: str = os.environ.get("EXTRA_ROLE_NAMES_FOR_INSTRUCTOR") or ""
    if extra_roles:
        extra_roles = extra_roles.lower().split(",")
        DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR.extend(extra_roles)
    return user_role.lower() in DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR
