"""Module for GFS model data on AWS Open Data."""
import logging
from datetime import datetime, timedelta, timezone

from defusedxml import ElementTree
from spin_http import Request, http_send

MODEL_HOUR_INTERVAL = 6
NUM_EXPECTED_FORECASTS = 209
S3_BUCKET = "noaa-gfs-bdp-pds"

logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def get_forecast_keys_from_s3_list_objects_resp(model_run: datetime) -> set[str]:
    """Get the forecast keys from the S3 list objects response.

    Args:
        model_run (datetime): a datetime object representing the model run time.

    Returns:
        set[str]: A set of forecast keys.
    """
    url = build_url(model_run=model_run)
    resp = http_send(Request("GET", url, [], None))
    root = ElementTree.fromstring(resp.body)

    xmlns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    available_keys = set()

    for key in root.iter(f"{xmlns}Key"):
        key_text = key.text
        if not key_text.endswith(".anl") and not key_text.endswith(".idx"):
            available_keys.add(key_text)

    return available_keys


def get_latest_complete_run() -> datetime | None:
    """Get the latest complete model run.

    Returns:
        Optional[datetime]: datetime representing the time of the latest complete run.
    """
    max_runs_to_try = 3
    latest_possible_run = calc_latest_possible_run(now=datetime.now(tz=timezone.utc))
    runs_to_try = [
        latest_possible_run - timedelta(hours=i * MODEL_HOUR_INTERVAL)
        for i in range(max_runs_to_try)
    ]

    for run in runs_to_try:
        forecasts = get_forecast_keys_from_s3_list_objects_resp(model_run=run)
        num_forecasts = len(forecasts)
        if num_forecasts == NUM_EXPECTED_FORECASTS:
            logging.info(
                "Found COMPLETE (%d forecasts) run: %s",
                num_forecasts,
                run.isoformat(),
            )
            return run
        logging.info(
            "Found incomplete (%d forecasts) run: %s",
            num_forecasts,
            run.isoformat(),
        )
    return None


def build_s3_grib_file_prefix(model_run: datetime) -> str:
    """Build the S3 prefix for the GRIB files for the given model run.

    Args:
        model_run (datetime): The model run time.

    Returns:
        str: The S3 prefix.
    """
    year = model_run.year
    month = model_run.month
    day = model_run.day
    hour = model_run.hour
    return f"gfs.{year}{month:02}{day:02}/{hour:02}/atmos/gfs.t{hour:02}z.pgrb2.0p25"


def build_url(model_run: datetime) -> str:
    """Build the S3 list objects URL for the given model run.

    Args:
        model_run (datetime): The model run time.

    Returns:
        str: The S3 list objects URL.
    """
    prefix = build_s3_grib_file_prefix(model_run=model_run)
    return f"https://{S3_BUCKET}.s3.amazonaws.com/?list-type=2&prefix={prefix}"


def calc_latest_possible_run(now: datetime) -> datetime:
    """Calculate the latest possible model run time.

    Args:
        now (datetime): The current time.

    Returns:
        datetime: The latest possible model run time.
    """
    estimated_model_delay = timedelta(hours=2)
    adjusted_base_time = now - estimated_model_delay
    hour = adjusted_base_time.hour
    run_hour = MODEL_HOUR_INTERVAL * (hour // MODEL_HOUR_INTERVAL)
    return datetime(
        year=adjusted_base_time.year,
        month=adjusted_base_time.month,
        day=adjusted_base_time.day,
        hour=run_hour,
        tzinfo=timezone.utc,
    )
