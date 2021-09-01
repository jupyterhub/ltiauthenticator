from tornado.log import app_log
from tornado.web import RequestHandler


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
