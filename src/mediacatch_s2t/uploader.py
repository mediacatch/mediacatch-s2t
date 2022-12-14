import json
import os
import pathlib

import pymediainfo
import requests

from mediacatch_s2t import (
    PRESIGNED_URL, TRANSCRIPT_URL, UPDATE_STATUS_URL, PROCESSING_TIME_RATIO
)


class UploaderException(Exception):
    pass


class Uploader:
    def __init__(self, file, api_key):
        self.file = file
        self.api_key = api_key
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
        return f"{TRANSCRIPT_URL}?id={self.file_id}&api_key={self.api_key}"

    def get_duration(self):
        """Get audio track duration of a file.

        :return
        tuple: (bool, duration_in_miliseconds)
        """
        try:
            mi = pymediainfo.MediaInfo.parse(self.file)
            if not mi.audio_tracks:
                return True, 0
            return True, mi.audio_tracks[0].duration
        except OSError:
            return False, 0
        except Exception:
            return False, 0

    def estimated_result_time(self, audio_length=0):
        """Estimated processing time in seconds"""

        if not isinstance(audio_length, int):
            return 0
        processing_time = PROCESSING_TIME_RATIO * audio_length
        return round(processing_time / 1000)

    def _get_upload_url(self, mime_file):
        response = self._make_post_request(
            url=PRESIGNED_URL,
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
            url=UPDATE_STATUS_URL,
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

        is_having_duration, file_duration = self.get_duration()
        if is_having_duration and not file_duration:
            result["status"] = "error"
            result["message"] = "The file doesn't have an audio track"
            return result

        mime_file = {
            "duration": file_duration,
            "filename": pathlib.Path(self.file).name,
            "file_ext": pathlib.Path(self.file).suffix,
            "filesize": os.path.getsize(self.file),
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


def upload_and_get_transcription(file, api_key):
    return Uploader(file, api_key).upload_file()
