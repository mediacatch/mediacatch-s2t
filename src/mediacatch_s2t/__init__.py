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
MULTIPLE_UPLOAD_ENDPOINT = (
    os.environ.get('MEDIACATCH_PRESIGN_CHUNK_ENDPOINT') or
    '/presigned-chunk-post-url'
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
