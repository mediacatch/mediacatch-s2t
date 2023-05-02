from unittest import mock

import pytest
import responses

from mediacatch_s2t import URL, MULTIPART_UPLOAD_CREATE_ENDPOINT
from mediacatch_s2t.uploader import ChunkedFileUploader


class TestMultipartUpload:
    create_multipart_url = f"{URL}{MULTIPART_UPLOAD_CREATE_ENDPOINT}"
    chunk_maxsize = 20480000
    filesize = (5 * chunk_maxsize) + 10000
    file_id = "644f6676997bc2477563246e"
    upload_id = "2~iRldDSPjP1cJCXg-7NmR9Sd4xpX_Cii"
    mime_file = {
        "duration": 1000,
        "filename": "file-test",
        "file_ext": ".mp4",
        "filesize": filesize,
        "language": "da",
    }

    @pytest.fixture(autouse=True)
    def _mock_pathlib_path(self):
        with mock.patch("pathlib.Path") as mock_Path:
            def side_effect():
                return True
            mock_Path.return_value.name = 'name'
            mock_Path.return_value.suffix = '.avi'
            mock_Path.return_value.is_file.side_effect = side_effect
            yield mock_Path

    @pytest.fixture(autouse=True)
    def _mock_os_getsize(self):
        with mock.patch("os.path.getsize") as mock_getsize:
            mock_getsize.return_value = self.filesize
            yield mock_getsize

    @pytest.fixture(autouse=True)
    def _mock_create_temp_dir_path(self):
        with mock.patch("mediacatch_s2t.uploader.ChunkedFileUploader._create_temp_dir_path") as mock_mkdtemp:
            mock_mkdtemp.return_value = "temp_folder"
            yield mock_mkdtemp
    @pytest.fixture(autouse=True)
    def _mock_builtins_open(self):
        with mock.patch("builtins.open", mock.mock_open(read_data="data")) as mock_open:
            yield mock_open

    @responses.activate
    def test_make_multipart_call_return_success(self):
        responses.add(
            responses.POST,
            self.create_multipart_url,
            status=200,
            json={
                "file_id": self.file_id,
                "chunk_maxsize": self.chunk_maxsize,
                "total_chunks": 5 + 1,
                "upload_id": self.upload_id
            }
        )
        file = ChunkedFileUploader(
            file='file-test.mp4',
            api_key='test-key'
        )
        result = file.create_multipart_upload(self.mime_file)
        assert result == {
            "file_id": self.file_id,
            "chunk_maxsize": self.chunk_maxsize,
            "total_chunks": 5 + 1,
            "upload_id": self.upload_id
        }

    def test_split_into_chunk_give_correct_number_and_filesize(self):
        pass

    def test_upload_a_chunk_part_return_success(self):
        pass

    def test_make_complete_upload_call_return_success(self):
        pass
