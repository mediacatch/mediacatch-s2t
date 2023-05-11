from unittest import mock

import responses

from mediacatch_s2t import helper


class TestHelper:
    @mock.patch('mediacatch_s2t.helper.version', return_value="0.1.1")
    def test_read_installed_version(self, mocker):
        assert helper.read_installed_version() == "0.1.1"

    def test_read_installed_version_package_not_found(self, monkeypatch):
        monkeypatch.setattr(
            helper, "_PACKAGE_NAME",
            "this-package-should-not-be-exists-de320b98-87d1-4d58-9e33-c3fdf7aca36b"
        )
        assert helper.read_installed_version() == "0.0.0"

    @responses.activate
    def test_check_latest_version(self):
        url = f"https://pypi.org/pypi/{helper._PACKAGE_NAME}/json"
        responses.add(
            responses.GET,
            url,
            json={
                'info': {
                    'version': "7.7.7"
                }
            }
        )
        assert helper.check_latest_version() == "7.7.7"

    @responses.activate
    def test_check_latest_version_json_not_found(self):
        url = f"https://pypi.org/pypi/{helper._PACKAGE_NAME}/json"
        responses.add(
            responses.GET,
            url,
            status=500
        )
        assert helper.check_latest_version() is None

    def test_get_last_updated_return_success(self):
        with mock.patch.dict(
                "os.environ",
                {"MEDIACATCH_S2T_LAST_UPDATE": "1683720830"}
        ):
            assert helper.get_last_updated() == 1683720830

    def test_get_last_updated_return_0(self):
        with mock.patch.dict(
                "os.environ",
                {"MEDIACATCH_S2T_LAST_UPDATE": "invalid-data"}
        ):
            assert helper.get_last_updated() == 0

    def test_update_myself_not_updating(self):
        with mock.patch("mediacatch_s2t.helper.get_last_updated", return_value=253402210800):
            assert helper.update_myself() is False

    @mock.patch("mediacatch_s2t.helper.set_last_update",
                         return_value=None)
    @mock.patch("mediacatch_s2t.helper.get_last_updated",
                         return_value=0)
    @mock.patch("mediacatch_s2t.helper.check_latest_version",
               return_value="1.0.7")
    @mock.patch("mediacatch_s2t.helper.read_installed_version",
                        return_value="0.0.1")
    @mock.patch("mediacatch_s2t.helper.subprocess.run")
    def test_update_myself_update_to_last_version(
            self, mocker_run, mocker_set_lu, mocker_get_lu, mocker_check_lv,
            mocker_read):
        assert helper.update_myself() is True


    @mock.patch("mediacatch_s2t.helper.read_installed_version",
                        return_value="8.8.1")
    @mock.patch("mediacatch_s2t.helper.check_latest_version",
                        return_value="8.8.1")
    @mock.patch("mediacatch_s2t.helper.get_last_updated",
                         return_value=0)
    @mock.patch("mediacatch_s2t.helper.set_last_update",
                         return_value=None)
    def test_update_myself_update_version_is_up_to_date(
            self, mocker_set_lu, mocker_get_lu, mocker_check_lv, mocker_read):
        assert helper.update_myself() is False
