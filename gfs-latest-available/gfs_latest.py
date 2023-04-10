"""Spin components to determin the latest available GFS run."""
import json
import logging
import os

from spin_http import Request, Response

from spinwx.gfs import get_latest_complete_run
from spinwx.spin_utils import parse_spin_headers

logging.basicConfig(
    format="%(levelname)s: %(asctime)s GFS-LATEST: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def handle_request(request: Request) -> Response:
    """Handle a request.

    Args:
        request (Request): The request.

    Returns:
        Response: The response.
    """
    logging.info(
        'Received Request: {"route": %s, "host": %s}',
        request.uri,
        request.headers[0][1],
    )

    logging.debug("Environment: %s", os.environ)
    header_dict = parse_spin_headers(request.headers)
    logging.debug("headers: %s", header_dict)
    latest_run = get_latest_complete_run()
    response = json.dumps(
        {
            "latest_run": latest_run.isoformat(),
        },
    )
    return Response(200, [("content-type", "text/plain")], bytes(response, "utf-8"))
