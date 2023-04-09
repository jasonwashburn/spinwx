"""Functions for working with grib files."""
from collections import defaultdict


def parse_idx(idx: str) -> dict:
    """Parse a GRIB idx file into a dict.

    Grib .idx files are used map individual GRIB messages to specific byte
    ranges in the GRIB file.

    Example format:
    1:0:d=2023040812:PRMSL:mean sea level:anl:
    2:1005022:d=2023040812:CLMR:1 hybrid level:anl:
    3:1115513:d=2023040812:ICMR:1 hybrid level:anl:

    Args:
        idx (str): The idx file contents.

    Returns:
        dict: The parsed idx file as a dict.
    """
    idx_dict: defaultdict[str, defaultdict] = defaultdict(lambda: defaultdict(dict))
    prev_start_byte = None
    for line in reversed(idx.splitlines()):
        _, start_byte, _, param, level, _ = line.rstrip(":").split(":")
        idx_dict[level][param]["byte_range"] = (int(start_byte), prev_start_byte)
        prev_start_byte = int(start_byte)
    return idx_dict
