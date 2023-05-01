import json
import os
import pathlib

import requests
import subprocess
import json
from typing import NamedTuple


from mediacatch_s2t import (
    URL,
    SINGLE_UPLOAD_ENDPOINT, TRANSCRIPT_ENDPOINT, UPDATE_STATUS_ENDPOINT,
    MULTIPART_UPLOAD_CREATE_ENDPOINT, MULTIPART_UPLOAD_URL_ENDPOINT,
    MULTIPART_UPLOAD_COMPLETE_ENDPOINT,
    PROCESSING_TIME_RATIO
)


class FFProbeResult(NamedTuple):
    return_code: int
    json: str
    error: str


class UploaderException(Exception):
    message = "Error when the uploader makes a post request."

    def __init__(self, cause=None):
        self.cause = cause

    def __str__(self):
        if self.cause:
            return "{}: {}".format(self.message, str(self.cause))
        else:
            return self.message


class UploaderBase:
    def __init__(self, file, api_key, language='da'):
        self.file = file
        self.api_key = api_key
        self.language = language
        self.file_id = None

    def _is_file_exist(self):
        return pathlib.Path(self.file).is_file()

    def _is_response_error(self, response):
        if response.status_code >= 400:
            if response.status_code == 401:
                return True, response.json()['message']
            return True, response.json()['message']
        return False, ''

    def _make_post_request(self, *args, **kwargs):
        try:
            response = requests.post(*args, **kwargs)
            is_error, msg = self._is_response_error(response)
            if is_error:
                raise Exception(msg)
            return response
        except Exception as e:
            raise UploaderException from e

    @property
    def _transcript_link(self):
        return f"{URL}{TRANSCRIPT_ENDPOINT}?id={self.file_id}&api_key={self.api_key}"

    @staticmethod
    def _ffprobe(file_path) -> FFProbeResult:
        command_array = ["ffprobe",
                        "-v", "quiet",
                        "-print_format", "json",
                        "-show_format",
                        "-show_streams",
                        file_path]
        result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return FFProbeResult(return_code=result.returncode,
                            json=json.loads(result.stdout),
                            error=result.stderr)

    def get_duration(self):
        """Get audio track duration of a file.

        :return
        tuple: (duration_in_miliseconds, stream_json | error_msg)
        """
        try:
            probe = self._ffprobe(self.file)
            if probe.return_code:
                return 0, probe.error
            else:
                for stream in probe.json['streams']:
                    if stream['codec_type'] == 'audio':
                        return int(float(stream['duration']) * 1000), stream
                else:
                    return 0, "The file doesn't have an audio track"
        except OSError as e:
            return 0, 'FFmpeg not installed (sudo apt install ffmpeg)'

    def estimated_result_time(self, audio_length=0):
        """Estimated processing time in seconds"""

        if not isinstance(audio_length, int):
            return 0
        processing_time = PROCESSING_TIME_RATIO * audio_length
        return round(processing_time / 1000)

    def _get_upload_url(self, mime_file):
        response = self._make_post_request(
            url=f'{URL}{SINGLE_UPLOAD_ENDPOINT}',
            json=mime_file,
            headers={
                "Content-type": 'application/json',
                "X-API-KEY": self.api_key
            }
        )
        response_data = json.loads(response.text)
        url = response_data.get('url')
        data = response_data.get('fields')
        _id = response_data.get('id')
        return {
            "url": url,
            "fields": data,
            "id": _id
        }

    def _post_file(self, url, data):
        with open(self.file, 'rb') as f:
            response = self._make_post_request(
                url,
                data=data,
                files={'file': f}
            )
            return response

    def _get_transcript_link(self):
        self._make_post_request(
            url=f'{URL}{UPDATE_STATUS_ENDPOINT}',
            json={"id": self.file_id},
            headers={
                "Content-type": 'application/json',
                "X-API-KEY": self.api_key
            }
        )
        return self._transcript_link


class Uploader(UploaderBase):
    """Uploader Class

    This class is to send a file to the API server.
    The API server currently only allows file less than 4gb
    to be sent with this upload class.
    """

    def upload_file(self):
        result = {
            "url": "",
            "status": "",
            "estimated_processing_time": 0,
            "message": ""
        }
        if not self._is_file_exist():
            result["status"] = "error"
            result["message"] = "The file doesn't exist"
            return result

        file_duration, msg = self.get_duration()
        if not file_duration:
            result["status"] = "error"
            result["message"] = msg
            return result

        mime_file = {
            "duration": file_duration,
            "filename": pathlib.Path(self.file).name,
            "file_ext": pathlib.Path(self.file).suffix,
            "filesize": os.path.getsize(self.file),
            "language": self.language,
        }
        try:
            _upload_url = self._get_upload_url(mime_file)
            url = _upload_url.get('url')
            data = _upload_url.get('fields')
            self.file_id = _upload_url.get('id')

            self._post_file(url, data)
            transcript_link = self._get_transcript_link()
        except UploaderException as e:
            result["status"] = "error"
            result["message"] = str(e)
            return result

        result = {
            "url": transcript_link,
            "status": "uploaded",
            "estimated_processing_time": self.estimated_result_time(file_duration),
            "message": "The file has been uploaded."
        }
        return result


class ChunkedFileUploader(UploaderBase):
    """Multipart Uploader Class

    This class is to split a bigfile into chunked files, and send them
    with multipart upload method.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size: int = 0
        self.create_endpoint: str = f"{URL}{MULTIPART_UPLOAD_CREATE_ENDPOINT}"
        self.signed_url_endpoint: str = f"{URL}{MULTIPART_UPLOAD_URL_ENDPOINT}"
        self.complete_endpoint: str = f"{URL}{MULTIPART_UPLOAD_COMPLETE_ENDPOINT}"
        self.headers: dict = self._get_headers()
        self.result = {
            "url": "",
            "status": "",
            "estimated_processing_time": 0,
            "message": ""
        }

    def _get_headers(self) -> dict:
        return {
            "Content-type": "application/json",
            "X-API-KEY": self.api_key
        }

    def _set_result_error_message(self, msg) -> None:
        self.result["status"] = "error"
        self.result["message"] = msg

    def create_multipart_upload(self, mime_file: dict):
        response = self._make_post_request(
            url=self.create_endpoint,
            headers=self.headers,
            json=mime_file
        )
        data: dict = response.json()
        return {
            "chunk_maxsize": data["chunk_maxsize"],
            "file_id": data["file_id"],
            "total_chunks": data["total_chunks"],
            "upload_id": data["upload_id"]
        }

    def split_file_into_chunks(self):
        pass

    def upload_chunks(self):
        pass

    def send_upload_completed_message(self):
        pass

    def upload_file(self):
        if not self._is_file_exist():
            self._set_result_error_message("The file doesn't exist")
            return self.result

        file_duration, msg = self.get_duration()
        if not file_duration:
            self._set_result_error_message(msg)
            return self.result

        mime_file = {
            "duration": file_duration,
            "filename": pathlib.Path(self.file).name,
            "file_ext": pathlib.Path(self.file).suffix,
            "filesize": os.path.getsize(self.file),
            "language": self.language,
        }
        try:
            meta = self.create_multipart_upload(mime_file)
            chunk_maxsize = meta["chunk_maxsize"],
            file_id = meta["file_id"],
            total_chunks = meta["total_chunks"],
            upload_id = meta["upload_id"]


        except UploaderException as e:
            self._set_result_error_message(str(e))
            return self.result

        self.result = {
            "url": "",
            "status": "uploaded",
            "estimated_processing_time": self.estimated_result_time(file_duration),
            "message": "The file has been uploaded."
        }
        return self.result


def upload_and_get_transcription(file, api_key, language):
    return Uploader(file, api_key, language).upload_file()
