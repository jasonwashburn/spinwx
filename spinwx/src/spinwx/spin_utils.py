"""Common utility functions to make up for limitations in the spin python sdk."""
from spin_http import Request


def parse_spin_headers(headers: str) -> dict:
    """Parse the headers from a spin request.

    Args:
        headers (str): The headers from a spin request.

    Returns:
        dict: The headers as a dict.
    """
    header_dict = {}
    for pair in headers:
        header_dict[pair[0]] = pair[1]
    return header_dict


def get_path_params_from_spin_path_info(spin_path_info: str) -> list:
    """Get the path params from the spin path info.

    Args:
        spin_path_info (str): The spin path info.

    Returns:
        list: The path params.
    """
    return spin_path_info.lstrip("/").split("/")


def get_request_info(request: Request) -> dict:
    """Get the various information from a spin request.

    Useful for debugging.

    Args:
        request (Request): The spin request.

    Returns:
        dict: The request info.
    """
    header_dict = parse_spin_headers(request.headers)
    if spin_path_info := header_dict.get("spin-path-info"):
        path_params = get_path_params_from_spin_path_info(spin_path_info)
    else:
        path_params = None
    uri = request.uri
    return {
        "uri": uri,
        "path_params": path_params,
        "headers": header_dict,
        "body": request.body.decode("utf-8"),
    }
