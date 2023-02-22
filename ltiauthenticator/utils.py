import logging
import re
from typing import Any, Dict, List

from tornado.web import RequestHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def normalize_string(name: str) -> str:
    """
    Function used to strip special characters and convert strings
    to docker container compatible names. This function is used mostly
    with course labels, as they are used for the shared grader notebook
    container names.

    Args:
        name: The string to normalize for docker container and volume
        names (e.g. Dev-JupyterHub)

    Returns:
        normalized_name: The normalized string
    """
    if not name:
        raise ValueError("Name is empty")
    # truncate name after 30th character
    name = (name[:25] + "") if len(name) > 30 else name
    # remove special characters
    name = re.sub(r"[^\w-]+", "", name)
    # if the first character is any of _.- remove it
    name = name.lstrip("_.-")
    # convert to lower case
    name = name.lower()
    # limit course_id to 25 characters, since its used for o/s username
    # in jupyter/docker-stacks compatible grader notebook (NB_USER)
    normalized_name = name[0:25]
    logger.debug(f"String normalized to {normalized_name}")
    return normalized_name


def email_to_username(email: str) -> str:
    """
    Normalizes an email to get a username. This function
    calculates the username by getting the string before the
    @ symbol, removing special characters, removing comments,
    converting string to lowercase, and adds 1 if the username
    has an integer value already in the string.

    Args:
        email: A valid email address

    Returns:
        username: A username string

    Raises:
        ValueError if email is empty
    """
    if not email:
        raise ValueError("email is missing")
    username = email.split("@")[0]
    username = username.split("+")[0]
    username = re.sub(r"\([^)]*\)", "", username)
    username = re.sub(r"[^\w-]+", "", username)
    username = username.lower()
    logger.debug(f"Username normalized to {username}")

    return username


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
