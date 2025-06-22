import json
import subprocess
import sys
from typing import Any


def get_mkv_metadata(input_file: str) -> dict[str, Any]:
    """
    Retrieves metadata from an MKV file using the mkvmerge tool.

    Args:
        input_file (str): The path to the MKV file from which to retrieve metadata.

    Returns:
        dict: A dictionary containing the metadata of the MKV file in JSON format.

    Raises:
        SystemExit: If the mkvmerge command fails, the program will exit with an error message.
    """
    command = [
        "mkvmerge",
        "--identify",
        input_file,
        "--identification-format",
        "json",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing mkvmerge: {result.stderr}")
        sys.exit(1)
    metadata = json.loads(result.stdout)
    return metadata
