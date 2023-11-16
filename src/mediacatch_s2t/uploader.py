import os
import requests
import threading
from abc import ABC
from pathlib import Path

from mediacatch_s2t import (
    URL,
    TRANSCRIPT_ENDPOINT,
    UPLOAD_CREATE_ENDPOINT, UPLOAD_URL_ENDPOINT, UPLOAD_COMPLETE_ENDPOINT
)
from mediacatch_s2t.helper import update_myself


class UploaderException(Exception):
    message = "Error from uploader module"

    def __init__(self, cause=None):
        self.cause = cause

    def __str__(self):
        if self.cause:
            return "{}: {}".format(self.message, str(self.cause))
        else:
            return self.message


class UploaderBase(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.result = {
            "url": "",
            "status": "",
            "estimated_processing_time": 0,
            "message": ""
        }

    def _get_headers(self) -> dict:
        return {
            "Content-type": "application/json",
            "X-API-KEY": self.api_key,
            "X-Quota": self.quota
        }

    def _is_file_exist(self):
        return self.file.is_file()

    def _make_request(self, type, *args, **kwargs):
        """Make post request with retry mechanism."""
        call_limit = 3
        is_error, msg = True, "Have not made a request call."
        for _call in range(call_limit):
            if type == 'get':
                response = requests.get(*args, **kwargs)
            elif type == 'post':
                response = requests.post(*args, **kwargs)
            is_error, msg = self._is_response_error(response)
            if not is_error:
                break
        if is_error:
            url = kwargs.get('url')
            if not url:
                url, *rest = args
            raise UploaderException(
                f"Error during post request {url}; {msg}"
            )
        return response
    
    def _is_response_error(self, response):
        if response.status_code >= 400:
            if response.status_code == 401:
                return True, response.json()['detail']
            return True, response.json()['detail']
        return False, ''

    def _set_result_error_message(self, msg) -> None:
        self.result["status"] = "error"
        self.result["message"] = msg

class Uploader(UploaderBase):
    def __init__(self, file, api_key, quota) -> None:
        super().__init__()
        self.file = Path(file)

        self.file_name = self.file.name
        self.file_extension = self.file.suffix
        self.file_size = os.path.getsize(self.file)

        self.api_key = api_key
        self.quota = quota

        self.file_id: str = ""
        self.chunk_maxsize: int = 0
        self.upload_id: str = ""

        self.endpoint_create: str = f"{URL}{UPLOAD_CREATE_ENDPOINT}"
        self.endpoint_signed_url: str = f"{URL}{UPLOAD_URL_ENDPOINT}"
        self.endpoint_complete: str = f"{URL}{UPLOAD_COMPLETE_ENDPOINT}"
        self.headers: dict = self._get_headers()

        self.etags: list = []

    def start_file_upload(self, mime_file: dict) -> dict:
        response = self._make_request(
            type='post',
            url=self.endpoint_create,
            headers=self.headers,
            json=mime_file
        )
        data: dict = response.json()
        return data["file_id"]

    def chop_and_upload_chunk(self) -> None:
        threads = []
        with open(self.file, 'rb') as f:
            part_number = 1
            while True:
                chunk_size = 100 * 1024 * 1024
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                thread = threading.Thread(target=self.upload_part,
                                          args=(part_number, chunk))
                threads.append(thread)
                thread.start()
                part_number += 1
        for thread in threads:
            thread.join()
        return None

    def _upload_data_chunk_to_bucket(self, url: str, file_data: bytes) -> str:
        response: requests.Response = requests.put(url=url, data=file_data)
        etag: str = response.headers['ETag']
        return etag

    def upload_part(self, part_number: int, file_data: bytes) -> None:
        response = self._make_request(
            type='get',
            url=self.endpoint_signed_url.format(file_id=self.file_id, part_number=part_number),
            headers=self.headers,
        ).json()
        etag = self._upload_data_chunk_to_bucket(response['url'], file_data)
        self.etags.append({'e_tag': etag, 'part_number': part_number})
        return None

    def complete_the_upload(self) -> bool:
        response: requests.Response = self._make_request(
            type='post',
            url=self.endpoint_complete.format(file_id=self.file_id),
            headers=self.headers,
            json={"parts": self.etags}
        )
        if response.status_code != 201:
            return False
        return True

    def upload_file(self):
        if not self._is_file_exist():
            self._set_result_error_message("The file doesn't exist")
            return self.result

        mime_file = {
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "quota": self.quota,
        }
        try:
            self.file_id = self.start_file_upload(mime_file)

            self.chop_and_upload_chunk()
            self.complete_the_upload()
        except Exception as e:
            self._set_result_error_message(str(e))
            return self.result

        self.result = {
            "url": URL + TRANSCRIPT_ENDPOINT.format(file_id=self.file_id),
            "status": "uploaded",
            "estimated_processing_time": 0,
            "message": "The file has been uploaded."
        }
        return self.result


def upload_and_get_transcription(file, api_key, quota) -> dict:
    result: dict = Uploader(file, api_key, quota).upload_file()
    update_myself()
    return result
