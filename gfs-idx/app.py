"""The base component of the spinwx package."""
from spin_http import Request, Response


def handle_request(request: Request) -> Response:
    """Handle a request for the spinwx package."""
    return Response(
        200,
        [("content-type", "text/plain")],
        bytes(f"Hello!\nRequest: {request}", "utf-8"),
    )
