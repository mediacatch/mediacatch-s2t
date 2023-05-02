"""MediaCatch speech-to-text file uploader.

"""

# Version of the mc-s2t-mediacatch_s2t
__version__ = "0.0.4"

import os

URL = (
    os.environ.get('MEDIACATCH_URL') or
    'https://s2t.mediacatch.io'
)

SINGLE_UPLOAD_ENDPOINT = (
    os.environ.get('MEDIACATCH_PRESIGN_ENDPOINT') or
    '/presigned-post-url'
)
MULTIPART_UPLOAD_CREATE_ENDPOINT = (
    os.environ.get('MEDIACATCH_MULTIPART_UPLOAD_CREATE_ENDPOINT') or
    '/multipart-upload/id'
)
MULTIPART_UPLOAD_URL_ENDPOINT = (
    os.environ.get('MEDIACATCH_MULTIPART_UPLOAD_URL_ENDPOINT') or
    '/multipart-upload/url'
)
MULTIPART_UPLOAD_COMPLETE_ENDPOINT = (
    os.environ.get('MEDIACATCH_MULTIPART_UPLOAD_COMPLETE_ENDPOINT') or
    '/multipart-upload/complete'
)
UPDATE_STATUS_ENDPOINT = (
    os.environ.get('MEDIACATCH_UPDATE_STATUS_ENDPOINT') or
    '/upload-completed'
)
TRANSCRIPT_ENDPOINT = (
    os.environ.get('MEDIACATCH_TRANSCRIPT_ENDPOINT') or
    '/result'
)
PROCESSING_TIME_RATIO = 0.1
CHUNK_SIZE_MIN = 50 * 1024 * 1024
