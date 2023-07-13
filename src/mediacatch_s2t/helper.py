import os
import requests
import subprocess
from datetime import datetime
from typing import Union

from importlib_metadata import PackageNotFoundError, version


_PACKAGE_NAME: str = "mediacatch_s2t"
_UPDATE_DURATION: int = 24 * 60 * 60  # 24 hour


def read_installed_version() -> str:
    try:
        _version: str = version(_PACKAGE_NAME)
    except PackageNotFoundError:
        _version: str = '0.0.0'
    return _version


def check_latest_version() -> Union[str, None]:
    try:
        response = requests.get(f"https://pypi.org/pypi/{_PACKAGE_NAME}/json")
        latest_version: str = response.json()['info']['version']
    except (requests.exceptions.RequestException, KeyError, TypeError):
        latest_version: None = None
    return latest_version


def get_last_updated() -> int:
    _last_updated = os.environ.get('MEDIACATCH_S2T_LAST_UPDATE', 0)
    try:
        last_updated = int(_last_updated)
    except ValueError:
        last_updated = 0
    return last_updated


def set_last_update() -> None:
    timestamp_now: int = int(datetime.now().timestamp())
    os.environ['MEDIACATCH_S2T_LAST_UPDATE']: str = str(timestamp_now)
    return None


def update_myself() -> bool:
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
