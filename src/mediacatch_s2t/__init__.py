"""MediaCatch speech-to-text file uploader.

"""

# Version of the mc-s2t-mediacatch_s2t
__version__ = '1.9.9'

import os

URL: str = os.environ.get('MEDIACATCH_URL', 'https://s2t.mediacatch.io/api/v2')
UPLOAD_CREATE_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_UPLOAD_CREATE_ENDPOINT',
    '/upload/')
UPLOAD_URL_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_UPLOAD_URL_ENDPOINT',
    '/upload/{file_id}/{part_number}')
UPLOAD_COMPLETE_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_UPLOAD_COMPLETE_ENDPOINT',
    '/upload/{file_id}/complete')
TRANSCRIPT_ENDPOINT: str = os.environ.get(
    'MEDIACATCH_TRANSCRIPT_ENDPOINT',
    '/result/{file_id}')

ENABLE_AUTOMATIC_UPDATE: bool = True
