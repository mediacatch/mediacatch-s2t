# MediaCatch Speech-To-Text Uploader

![github test](https://github.com/mediacatch/mediacatch-s2t/actions/workflows/github-action.yml/badge.svg) [![codecov](https://codecov.io/gh/mediacatch/mediacatch-s2t/branch/main/graph/badge.svg?token=ZQ36ZRJ2ZU)](https://codecov.io/gh/mediacatch/mediacatch-s2t)

mediacatch-s2t is the [MediaCatch](https://mediacatch.io/) service for uploading a file in python and get the transcription result in a link. This module requires python3.7 or above.


You can use it on your CLI
```bash
pip install mediacatch_s2t

python -m mediacatch_s2t <path/to/your/media/file> <api_key>
```

Or import it as a module
```bash
from mediacatch_s2t.uploader import upload_and_get_transcription

result = upload_and_get_transcription('path/to/your/media/file', 'api_key')
```
