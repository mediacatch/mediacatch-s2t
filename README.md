# MediaCatch Speech-To-Text Uploader

![github test](https://github.com/mediacatch/mediacatch-s2t/actions/workflows/lint-and-pytest.yml/badge.svg) [![codecov](https://codecov.io/gh/mediacatch/mediacatch-s2t/branch/main/graph/badge.svg?token=ZQ36ZRJ2ZU)](https://codecov.io/gh/mediacatch/mediacatch-s2t)

mediacatch-s2t is the [MediaCatch](https://mediacatch.io/) service for uploading a file in python and get the transcription result in a link. This module requires python3.9 or above.


You can use it on your CLI
```bash
pip install mediacatch_s2t

python -m mediacatch_s2t <api_key> <path/to/your/media/file> --fallback_language <lang_code>
```

Or import it as a module
```python
from mediacatch_s2t.uploader import upload_and_get_transcription


'''
The result will be a JSON object:
{
  "url": "url-to-your-transcription",
  "status": "uploaded",
  "estimated_processing_time": "your-estimated-time-to-get-your-transcription-done",
  "message": "The file has been uploaded."
}

'''
result = upload_and_get_transcription('path/to/your/media/file', 'api_key', fallback_language='da')
```


