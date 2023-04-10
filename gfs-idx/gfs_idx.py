"""The base component of the spinwx package."""
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from spin_http import Request, Response, http_send

from spinwx.gfs import build_idx_file_url
from spinwx.grib import parse_idx
from spinwx.spin_utils import (
    get_path_params_from_spin_path_info,
    get_query_params_from_header_dict,
    parse_spin_headers,
)

logging.basicConfig(
    format="%(levelname)s: %(asctime)s GFS-IDX: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def handle_request(request: Request) -> Response:
    """Handle a request for the spinwx package."""
    logging.debug("Environment: %s", os.environ)
    header_dict = parse_spin_headers(request.headers)
    logging.debug("headers: %s", header_dict)
    path_params = get_path_params_from_spin_path_info(
        header_dict.get("spin-path-info", ""),
    )
    query_params = get_query_params_from_header_dict(header_dict)
    if path_params[0] == "latest":
        # TODO: Need to update to use host passed in at runtime.
        host = "/".join(header_dict.get("spin-full-url", "").split("/")[0:3])
        latest_url = f"{host}/gfs/latest"
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
    grib_url = idx_url.rstrip(".idx")
    idx_resp = http_send(Request("GET", idx_url, [], None))
    idx_body = idx_resp.body.decode("utf-8")
    full_idx_dict = parse_idx(idx_body)
    idx_dict = (
        {level: full_idx_dict.get(level)}
        if (level := query_params.get("level"))
        else full_idx_dict
    )

    valid_time = (run + timedelta(hours=forecast)).isoformat()
    response_dict = {
        "idx_url": idx_url,
        "grib_url": grib_url,
        "model_run": run.isoformat(),
        "forecast": f"+{forecast}",
        "valid_time": valid_time,
        "idx_data": idx_dict,
    }
    return Response(
        200,
        [("content-type", "application/json")],
        json.dumps(response_dict).encode("utf-8"),
    )
