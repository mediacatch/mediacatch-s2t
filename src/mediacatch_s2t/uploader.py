import json
import os
import pathlib

import requests
import subprocess
import json
from typing import NamedTuple


from mediacatch_s2t import (
    URL, PRESIGNED_ENDPOINT, TRANSCRIPT_ENDPOINT, UPDATE_STATUS_ENDPOINT, PROCESSING_TIME_RATIO
)

class FFProbeResult(NamedTuple):
    return_code: int
    json: str
    error: str

class UploaderException(Exception):
    pass


class Uploader:
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
            raise UploaderException(str(e))

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
                try:
                    for stream in probe.json['streams']:
                        if stream['codec_type'] == 'audio':
                            return int(float(stream['duration']) * 1000), stream
                    else:
                        return 0, "The file doesn't have an audio track"
                except:
                    if 'duration' in probe.json['format']:
                        return int(float(probe.json['format']['duration']) * 1000), probe.json['format']
                    else:
                        return 0, "Duration couldn't be found for audio track"
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
            url=f'{URL}{PRESIGNED_ENDPOINT}',
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


def upload_and_get_transcription(file, api_key, language):
    return Uploader(file, api_key, language).upload_file()
