import os
import requests
import subprocess
from datetime import datetime
from typing import Union

from importlib_metadata import PackageNotFoundError, version


_PACKAGE_NAME: str = "mediacatch_s2t"
_UPDATE_DURATION: int = 24 * 60 * 60  # 24 hour


def read_installed_version() -> str:
    """
    Reads and returns the installed version of the specified package.
    
    Returns:
        str: The installed version of the package. Returns '0.0.0' if the package is not found.
    """
    try:
        _version: str = version(_PACKAGE_NAME)
    except PackageNotFoundError:
        _version: str = '0.0.0'
    return _version


def check_latest_version() -> Union[str, None]:
    """
    Checks and returns the latest available version of the specified package from PyPI.
    
    Returns:
        Union[str, None]: The latest version available on PyPI. Returns None if there is a request exception or if the version information is not available.
    """
    try:
        response = requests.get(f"https://pypi.org/pypi/{_PACKAGE_NAME}/json")
        latest_version: str = response.json()['info']['version']
    except (requests.exceptions.RequestException, KeyError, TypeError):
        latest_version: None = None
    return latest_version


def get_last_updated() -> int:
    """
    Retrieves the timestamp of the last update from the environment variable.
    
    Returns:
        int: The timestamp of the last update. Returns 0 if the environment variable is not set or cannot be converted to an integer.
    """
    _last_updated = os.environ.get('MEDIACATCH_S2T_LAST_UPDATE', 0)
    try:
        last_updated = int(_last_updated)
    except ValueError:
        last_updated = 0
    return last_updated


def set_last_update() -> None:
    """
    Updates the environment variable 'MEDIACATCH_S2T_LAST_UPDATE' with the current timestamp.
    
    Returns:
        None
    """
    timestamp_now: int = int(datetime.now().timestamp())
    os.environ['MEDIACATCH_S2T_LAST_UPDATE']: str = str(timestamp_now)
    return None


def update_myself() -> bool:
    """
    Updates the package if a newer version is available and the last update was longer ago than the specified duration.

    Returns:
        bool: True if the package was updated, False otherwise.
    """
    timestamp_now = int(datetime.now().timestamp())
    timestamp_last_updated = get_last_updated()
    latest_update_in_seconds = timestamp_now - timestamp_last_updated
    if latest_update_in_seconds < _UPDATE_DURATION:
        return False

    current_version = read_installed_version()
    latest_version = check_latest_version()
    if latest_version and current_version < latest_version:
        subprocess.run([
            "python", "-m",
            "pip", "install",
            f"{_PACKAGE_NAME}", "-U", "--quiet"
        ])
        set_last_update()
        return True
    return False
