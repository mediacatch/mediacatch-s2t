from unittest import mock

import responses
from mediacatch_s2t import PRESIGNED_URL, TRANSCRIPT_URL, UPDATE_STATUS_URL
from mediacatch_s2t.uploader import upload_and_get_transcription, Uploader


@mock.patch("pathlib.Path.is_file", return_value=True)
def test_is_file_exist_mocked_return_true(mock_is_file):
    assert Uploader('fake file', 'fake key')._is_file_exist() is True


@mock.patch("pymediainfo.MediaInfo.parse")
def test_get_duration_mocked_return_value(mock_pymedia):
    class MockDuration:
        duration = 1000
    mock_pymedia.return_value.audio_tracks = [MockDuration]
    assert Uploader('fake file', 'fake key').get_duration() == (True, 1000)


def test_estimated_result_time():
    assert Uploader('fake file', 'fake key').estimated_result_time(1000) == 1

@responses.activate
@mock.patch("builtins.open", new_callable=mock.mock_open,
            read_data="bytes of data")
@mock.patch("pathlib.Path")
@mock.patch("os.path.getsize", return_value=100)
@mock.patch("pymediainfo.MediaInfo.parse")
def test_upload_succeed(mock_pymedia, mock_getsize, mock_Path, mock_open):
    URL_EXAMPLE = 'http://url-for-upload.example.com'

    def side_effect():
        return True
    mock_Path.return_value.name = 'name'
    mock_Path.return_value.suffix = '.avi'
    mock_Path.return_value.is_file.side_effect = side_effect

    class MockDuration:
        duration = 100000
    mock_pymedia.return_value.audio_tracks = [MockDuration]

    responses.add(
        responses.POST, PRESIGNED_URL, status=200,
        json={
            'url': URL_EXAMPLE,
            'fields': {'key': 'all fields we need'},
            'id': 'some-id'
        }
    )
    responses.add(
        responses.POST, UPDATE_STATUS_URL, status=204
    )
    responses.add(
        responses.POST, TRANSCRIPT_URL, status=200
    )
    responses.add(
        responses.POST, URL_EXAMPLE, status=200
    )
    expected_output = {
        'estimated_processing_time': 75,
        'message': 'The file has been uploaded.',
        'status': 'uploaded',
        'url': 'https://s2t.mediacatch.io/result?id=some-id&api_key=fake-key'
    }
    assert Uploader('fake-file', 'fake-key').upload_file() == expected_output

