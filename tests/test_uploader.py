from unittest import mock

import responses
from mediacatch_s2t import URL, SINGLE_UPLOAD_ENDPOINT, TRANSCRIPT_ENDPOINT, UPDATE_STATUS_ENDPOINT
from mediacatch_s2t.uploader import upload_and_get_transcription, Uploader


@mock.patch("pathlib.Path.is_file", return_value=True)
def test_is_file_exist_mocked_return_true(mock_is_file):
    assert Uploader('fake file', 'fake key')._is_file_exist() is True


@mock.patch("subprocess.run")
def test_get_duration_mocked_return_value(mock_subprocess):
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = '{"streams": [{"codec_type": "audio", "duration": 1}]}'
    mock_subprocess.return_value.stderr = None
    assert Uploader('fake file', 'fake key').get_duration() == (1000, {'codec_type': 'audio', 'duration': 1})


def test_estimated_result_time():
    assert Uploader('fake file', 'fake key').estimated_result_time(10000) == 1

@responses.activate
@mock.patch("builtins.open", new_callable=mock.mock_open,
            read_data="bytes of data")
@mock.patch("pathlib.Path")
@mock.patch("os.path.getsize", return_value=100)
@mock.patch("subprocess.run")
def test_upload_succeed(mock_subprocess, mock_getsize, mock_Path, mock_open):
    URL_EXAMPLE = 'http://url-for-upload.example.com'

    def side_effect():
        return True
    mock_Path.return_value.name = 'name'
    mock_Path.return_value.suffix = '.avi'
    mock_Path.return_value.is_file.side_effect = side_effect

    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = '{"streams": [{"codec_type": "audio", "duration": 100}]}'
    mock_subprocess.return_value.stderr = None

    responses.add(
        responses.POST, f'{URL}{SINGLE_UPLOAD_ENDPOINT}', status=200,
        json={
            'url': URL_EXAMPLE,
            'fields': {'key': 'all fields we need'},
            'id': 'some-id'
        }
    )
    responses.add(
        responses.POST, f'{URL}{UPDATE_STATUS_ENDPOINT}', status=204
    )
    responses.add(
        responses.POST, f'{URL}{TRANSCRIPT_ENDPOINT}', status=200
    )
    responses.add(
        responses.POST, URL_EXAMPLE, status=200
    )
    expected_output = {
        'estimated_processing_time': 10,
        'message': 'The file has been uploaded.',
        'status': 'uploaded',
        'url': 'https://s2t.mediacatch.io/result?id=some-id&api_key=fake-key'
    }
    assert Uploader('fake-file', 'fake-key', 'fake-language').upload_file() == expected_output

