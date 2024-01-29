# MediaCatch Speech-To-Text Uploader

![github test](https://github.com/mediacatch/mediacatch-s2t/actions/workflows/lint-and-pytest.yml/badge.svg) [![codecov](https://codecov.io/gh/mediacatch/mediacatch-s2t/branch/main/graph/badge.svg?token=ZQ36ZRJ2ZU)](https://codecov.io/gh/mediacatch/mediacatch-s2t)

mediacatch-s2t is the [MediaCatch](https://mediacatch.io/) service for uploading a file in python and get the transcription result in a link. This module requires python3.9 or above.

<details>
    <summary>Supported languages</summary>

- af (Afrikaans)
- am (Amharic)
- ar (Arabic)
- as (Assamese)
- az (Azerbaijani)
- ba (Bashkir)
- be (Belarusian)
- bg (Bulgarian)
- bn (Bengali)
- bo (Tibetan)
- br (Breton)
- bs (Bosnian)
- ca (Catalan)
- cs (Czech)
- cy (Welsh)
- da (Danish)
- de (German)
- el (Greek)
- en (English)
- es (Spanish)
- et (Estonian)
- eu (Basque)
- fa (Persian)
- fi (Finnish)
- fo (Faroese)
- fr (French)
- gl (Galician)
- gu (Gujarati)
- ha (Hausa)
- haw (Hawaiian)
- he (Hebrew)
- hi (Hindi)
- hr (Croatian)
- ht (Haitian Creole)
- hu (Hungarian)
- hy (Armenian)
- id (Indonesian)
- is (Icelandic)
- it (Italian)
- ja (Japanese)
- jw (Javanese)
- ka (Georgian)
- kk (Kazakh)
- km (Khmer)
- kn (Kannada)
- ko (Korean)
- la (Latin)
- lb (Luxembourgish)
- ln (Lingala)
- lo (Lao)
- lt (Lithuanian)
- lv (Latvian)
- mg (Malagasy)
- mi (Maori)
- mk (Macedonian)
- ml (Malayalam)
- mn (Mongolian)
- mr (Marathi)
- ms (Malay)
- mt (Maltese)
- my (Burmese)
- ne (Nepali)
- nl (Dutch)
- nn (Norwegian Nynorsk)
- no (Norwegian)
- oc (Occitan)
- pa (Punjabi)
- pl (Polish)
- ps (Pashto)
- pt (Portuguese)
- ro (Romanian)
- ru (Russian)
- sa (Sanskrit)
- sd (Sindhi)
- si (Sinhala)
- sk (Slovak)
- sl (Slovene)
- sn (Shona)
- so (Somali)
- sq (Albanian)
- sr (Serbian)
- su (Sundanese)
- sv (Swedish)
- sw (Swahili)
- ta (Tamil)
- te (Telugu)
- tg (Tajik)
- th (Thai)
- tk (Turkmen)
- tl (Tagalog)
- tr (Turkish)
- tt (Tatar)
- uk (Ukrainian)
- ur (Urdu)
- uz (Uzbek)
- vi (Vietnamese)
- yi (Yiddish)
- yo (Yoruba)
- zh (Chinese)
- yue (Cantonese)

</details>

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


