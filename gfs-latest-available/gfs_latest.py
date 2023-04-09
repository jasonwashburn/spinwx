"""Spin components to determin the latest available GFS run."""
import json
import logging

from spin_http import Request, Response

from spinwx.gfs import get_latest_complete_run


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
    latest_run = get_latest_complete_run()
    response = json.dumps(
        {
            "latest_run": latest_run.isoformat(),
        },
    )
    return Response(200, [("content-type", "text/plain")], bytes(response, "utf-8"))
