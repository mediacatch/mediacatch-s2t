import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Generator

from mediacatch_s2t import (
    URL,
    TRANSCRIPT_ENDPOINT,
    UPLOAD_CREATE_ENDPOINT, UPLOAD_URL_ENDPOINT, UPLOAD_COMPLETE_ENDPOINT
)
from mediacatch_s2t.helper import update_myself


class UploaderException(Exception):
    """Custom exception class for handling errors within the Uploader class.
    
    Attributes:
        message (str): The error message to be displayed.
        cause (Exception, optional): The original exception that caused this error, if any.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(f"{message}: {str(cause)}" if cause else message)


class Uploader:
    """Handles the uploading of files to a server and manages the file upload process.

    Attributes:
        file_path (Path): Path of the file to be uploaded.
        api_key (str): API key for authentication.
        quota (int): Quota limit for the user.
        file_id (str): Unique identifier for the file once uploaded.
        etags (list): List of ETag values for each uploaded chunk.
        endpoints (dict): Endpoints for file creation, signed URL generation, and completion.
        headers (dict): Headers to be used for HTTP requests.
    """

    CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
    REQUEST_RETRY_LIMIT = 3

    def __init__(self, file: str, api_key: str, quota: Optional[str] = None, max_threads: int = 5) -> None:
        self.file_path = Path(file)
        if not self.file_path.is_file():
            raise FileNotFoundError(f"The file {file} does not exist")

        self.api_key = api_key
        self.quota = quota
        self.file_id = ""
        self.etags = []
        self.endpoints = {
            "create": f"{URL}{UPLOAD_CREATE_ENDPOINT}",
            "signed_url": f"{URL}{UPLOAD_URL_ENDPOINT}",
            "complete": f"{URL}{UPLOAD_COMPLETE_ENDPOINT}",
            "result": f"{URL}{TRANSCRIPT_ENDPOINT}"
        }
        self.headers = {
            "Content-type": "application/json",
            "X-API-KEY": self.api_key,
            "X-Quota": str(self.quota)
        }
        self.max_threads = max_threads

    def upload_file(self) -> dict[str, str]:
        """Initiates and manages the file upload process.

        Returns:
            dict[str, str]: A dictionary containing the result of the upload process.
        """
        try:
            self.file_id = self.initiate_file_upload()
            self.upload_file_chunks()
            self.finalize_upload()
            return self.get_upload_result()
        except Exception as e:
            raise UploaderException("Failed to upload file", e)

    def initiate_file_upload(self) -> str:
        """Starts the file upload process by creating a new upload session on the server.

        Returns:
            str: The file ID assigned by the server.
        """
        mime_file = {
            "file_name": self.file_path.name,
            "file_extension": self.file_path.suffix,
            "quota": self.quota,
        }
        response = self._make_request('post', self.endpoints['create'], json=mime_file)
        return response.json()["file_id"]

    def upload_file_chunks(self) -> None:
        """Splits the file into chunks and uploads each chunk to the server in parallel."""
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor, self.file_path.open('rb') as file:
            futures = {executor.submit(self.upload_chunk, part_number, chunk): part_number 
                       for part_number, chunk in enumerate(self._read_file_in_chunks(file), start=1)}

            for future in as_completed(futures):
                part_number = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Chunk {part_number} failed to upload due to: {e}")

    def _read_file_in_chunks(self, file) -> Generator[bytes, None, None]:
        """Generator that reads the file in chunks.

        Args:
            file (IO[bytes]): File object opened in binary read mode.

        Yields:
            bytes: A chunk of the file.
        """
        while True:
            chunk = file.read(self.CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

    def upload_chunk(self, part_number: int, chunk: bytes) -> None:
        """Uploads a single chunk of the file to the server.

        Args:
            part_number (int): The part number of the chunk in the sequence.
            chunk (bytes): The file data to upload.
        """
        signed_url_response = self._make_request(
            'get',
            self.endpoints['signed_url'].format(file_id=self.file_id, part_number=part_number)
        )
        signed_url = signed_url_response.json()['url']
        etag = self._upload_chunk_to_storage(signed_url, chunk)
        self.etags.append({'e_tag': etag, 'part_number': part_number})

    def _upload_chunk_to_storage(self, url: str, chunk: bytes) -> str:
        """Uploads a chunk of data to a given URL.

        Args
                    (url (str): The URL to which the chunk will be uploaded.
            chunk (bytes): The chunk of data to be uploaded.

        Returns:
            str: The ETag header value returned by the server, identifying the chunk.
        """
        response = requests.put(url, data=chunk)
        return response.headers['ETag']

    def finalize_upload(self) -> None:
        """Finalizes the file upload process, indicating all chunks have been uploaded."""
        response = self._make_request(
            'post',
            self.endpoints['complete'].format(file_id=self.file_id),
            json={"parts": self.etags}
        )
        self.estimated_processing_time = response.json()['estimated_processing_time']

    def get_upload_result(self) -> dict[str, str]:
        """Constructs the final result of the file upload process.

        Returns:
            dict[str, str]: A dictionary containing details of the upload, including the file URL.
        """
        return {
            "url": self.endpoints['result'].format(file_id=self.file_id),
            "status": "uploaded",
            "estimated_processing_time": self.estimated_processing_time,
            "message": "The file has been uploaded."
        }

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Makes an HTTP request with the specified method, URL, and additional arguments.

        Args:
            method (str): The HTTP method to use (e.g., 'get', 'post').
            url (str): The URL for the request.
            **kwargs: Additional keyword arguments to pass to the requests function.

        Returns:
            requests.Response: The response object from the HTTP request.

        Raises:
            UploaderException: If the request fails after the maximum retry limit.
        """
        for _ in range(self.REQUEST_RETRY_LIMIT):
            response = getattr(requests, method)(url, headers=self.headers, **kwargs)
            if self._is_response_successful(response):
                return response
            if method == 'post' and response.status_code >= 400:
                raise UploaderException(f"Error during request to {url}", response.json()['detail'])
        raise UploaderException("Maximum retry limit reached for request", None)

    @staticmethod
    def _is_response_successful(response: requests.Response) -> bool:
        """Checks if an HTTP response indicates a successful request.

        Args:
            response (requests.Response): The response object to check.

        Returns:
            bool: True if the response indicates success, False otherwise.
        """
        return 200 <= response.status_code < 300

def upload_and_get_transcription(file: str, api_key: str, quota: Optional[str] = None) -> dict[str, str]:
    """Uploads a file and returns its transcription.

    Args:
        file (str): The path to the file to be uploaded.
        api_key (str): The API key for authentication.
        quota (str | None): The quota to bill transcription hours from. Use None if user only has 1 quota.

    Returns:
        dict[str, str]: A dictionary containing the transcription or error message.

    Raises:
        UploaderException: If there's an issue with the file upload.
    """
    try:
        uploader = Uploader(file, api_key, quota)
        result = uploader.upload_file()
    except FileNotFoundError as fnfe:
        return {"status": "error", "message": str(fnfe)}
    except UploaderException as ue:
        return {"status": "error", "message": str(ue)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    update_myself()
    return result