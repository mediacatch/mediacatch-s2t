"""MediaCatch speech-to-text file uploader.

"""

# Version of the mc-s2t-mediacatch_s2t
__version__ = '0.0.9'

import os

URL: str = os.environ.get('MEDIACATCH_URL', 'https://s2t.mediacatch.io')
SINGLE_UPLOAD_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_PRESIGN_ENDPOINT',
    '/presigned-post-url')
MULTIPART_UPLOAD_CREATE_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_MULTIPART_UPLOAD_CREATE_ENDPOINT',
    '/multipart-upload/id')
MULTIPART_UPLOAD_URL_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_MULTIPART_UPLOAD_URL_ENDPOINT',
    '/multipart-upload/url')
MULTIPART_UPLOAD_COMPLETE_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_MULTIPART_UPLOAD_COMPLETE_ENDPOINT',
    '/multipart-upload/complete')
UPDATE_STATUS_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_UPDATE_STATUS_ENDPOINT',
    '/upload-completed')
TRANSCRIPT_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_TRANSCRIPT_ENDPOINT', '/result')
PROCESSING_TIME_RATIO: float = 0.1
MULTIPART_FILESIZE: int = 1 * 1024 * 1024 * 1024

ENABLE_AUTOMATIC_UPDATE: bool = True
