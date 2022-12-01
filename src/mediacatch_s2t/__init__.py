"""MediaCatch speech-to-text file uploader.

"""

# Version of the mc-s2t-mediacatch_s2t
__version__ = "0.0.2"

import os

PRESIGNED_URL = (
    os.environ.get('MEDIACATCH_PRESIGN_URL') or
    'https://s2t.mediacatch.io/presigned-post-url'
)
UPDATE_STATUS_URL = (
    os.environ.get('MEDIACATCH_UPDATE_STATUS_URL') or
    'https://s2t.mediacatch.io/upload-completed'
)
TRANSCRIPT_URL = (
    os.environ.get('MEDIACATCH_TRANSCRIPT_URL') or
    'https://s2t.mediacatch.io/result'
)
PROCESSING_TIME_RATIO = 0.1
