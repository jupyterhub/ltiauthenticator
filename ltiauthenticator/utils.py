import re

from tornado.log import app_log
from tornado.web import RequestHandler


def normalize_string(name: str) -> str:
    """
    Function used to strip special characters and convert strings
    to docker container and Kubernetes compatible names.

    Args:
        name: The string to normalize

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
    app_log.debug("String normalized to %s" % normalized_name)
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
    app_log.debug("String normalized to %s" % username)
    return username


def get_client_protocol(handler: RequestHandler) -> dict:
    """
    Gets first protocol from the x-forwarded-proto header that should
    represent the client's original http/https request.

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
    app_log.debug("First protocol from x-forwarded-proto list: %s" % protocol)
    return protocol


def convert_request_to_dict(arguments: dict) -> dict:
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
    app_log.debug("Request converted to dict: %s" % args)
    return args
