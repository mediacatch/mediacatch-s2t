import pytest

from mediacatch_s2t.uploader import UploaderException


class TestUploaderException:
    def test_UploaderException_without_cause(self):
        new_exception = UploaderException()
        assert str(new_exception) == "Error from uploader module"

    def test_UploderException_with_cause(self):
        new_exception = UploaderException("Test Exception")
        assert str(new_exception) == (
            "Error from uploader module: Test Exception"
        )
