"""A component to facilitate the retrieval of GFS grib data."""
import json
import logging

from spin_http import Request, Response, http_send

from spinwx.spin_utils import parse_spin_headers

logging.basicConfig(
    format="%(levelname)s: %(asctime)s GFS-IDX: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def handle_request(request: Request) -> Response:
    """Retrieve GFS data from AWS Open Data for query parameters.

    Args:
        request: The request to handle.

    Returns:
            A response containing the grib data.
    """
    header_dict = parse_spin_headers(request.headers)
    host = "/".join(header_dict.get("spin-full-url", "").split("/")[0:3])
    idx_url = f"{host}/gfs/idx/latest/0?level=surface"

    resp = http_send(Request("GET", idx_url, [], None))
    logging.debug("idx_body: %s", resp.body.decode("utf-8"))
    resp_dict = json.loads(resp.body.decode("utf-8"))
    tmp_dict = resp_dict.get("idx_data").get("surface").get("TMP")
    start_byte = tmp_dict.get("byte_range")[0]
    end_byte = tmp_dict.get("byte_range")[1]
    grib_url = resp_dict.get("grib_url")
    grib_message = http_send(
        Request("GET", grib_url, [("Range", f"bytes={start_byte}-{end_byte}")], None),
    )
    return Response(
        200,
        [("content-type", "text/plain")],
        bytes(f"{grib_message.body}", "utf-8"),
    )
