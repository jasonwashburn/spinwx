"""The base component of the spinwx package."""
import json
import logging
from datetime import datetime, timezone
from pprint import pformat

from spin_http import Request, Response, http_send

from spinwx.gfs import build_idx_file_url
from spinwx.grib import parse_idx
from spinwx.spin_utils import (
    get_path_params_from_spin_path_info,
    parse_spin_headers,
)

logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def handle_request(request: Request) -> Response:
    """Handle a request for the spinwx package."""
    header_dict = parse_spin_headers(request.headers)
    logging.debug("headers: %s", pformat(header_dict))
    path_params = get_path_params_from_spin_path_info(
        header_dict.get("spin-path-info", ""),
    )
    if path_params[0] == "latest":
        latest_url = "http://127.0.0.1:3000/gfs/latest"
        logging.debug("Sending request to %s", latest_url)
        latest_resp = http_send(Request("GET", latest_url, [], None))
        run = datetime.fromisoformat(
            json.loads(latest_resp.body.decode("utf-8")).get("latest_run"),
        )
        forecast = int(path_params[1])
    else:
        year = int(path_params[0])
        month = int(path_params[1])
        day = int(path_params[2])
        hour = int(path_params[3].lower().rstrip("z"))
        run = datetime(year, month, day, hour, tzinfo=timezone.utc)
        forecast = int(path_params[4].lower().lstrip("fh"))
    idx_url = build_idx_file_url(model_run=run, forecast=forecast)
    idx_resp = http_send(Request("GET", idx_url, [], None))
    idx_body = idx_resp.body.decode("utf-8")
    idx_dict = parse_idx(idx_body)
    response_dict = {"idx_url": idx_url, "idx_data": idx_dict}
    return Response(
        200,
        [("content-type", "application/json")],
        json.dumps(response_dict).encode("utf-8"),
    )
