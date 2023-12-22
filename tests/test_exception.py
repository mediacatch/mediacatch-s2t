import pytest

from mediacatch_s2t.uploader import UploaderException


class TestUploaderException:
    def test_UploaderException_without_cause(self):
        new_exception = UploaderException('Test message')
        assert str(new_exception) == 'Test message'

    def test_UploderException_with_cause(self):
        new_exception = UploaderException('Test message', 'Test Exception')
        assert str(new_exception) == (
            "Test message: Test Exception"
        )
