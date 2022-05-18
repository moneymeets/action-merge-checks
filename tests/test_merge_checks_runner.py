from unittest import TestCase
from unittest.mock import patch

from merge_checks import runner
from merge_checks.runner import Commit, Status, run


@patch.object(runner, "get_commit_checks_result")
@patch.object(runner, "get_commit_and_status")
@patch.object(runner, "set_commit_status")
class MergeChecksRunnerTest(TestCase):
    def test_result_state_success(
        self,
        mock_set_commit_status,
        mock_get_commit_and_status,
        mock_get_commit_checks_result,
    ):
        mock_get_commit_and_status.return_value = (
            Commit(repository="test", commit_sha="123", token="456"),
            Status(status_name="test status", details_url="example.com"),
        )
        mock_get_commit_checks_result.return_value = (True, "test summary")

        run()

        mock_get_commit_checks_result.assert_called_once()
        self.assertEqual("pending", mock_set_commit_status.call_args_list[0].kwargs.get("state"))
        mock_get_commit_checks_result.assert_called_once()
        self.assertEqual("success", mock_set_commit_status.call_args_list[1].kwargs.get("state"))

    def test_result_state_failure(
        self,
        mock_set_commit_status,
        mock_get_commit_and_status,
        mock_get_commit_checks_result,
    ):
        mock_get_commit_and_status.return_value = (
            Commit(repository="test", commit_sha="123", token="456"),
            Status(status_name="test status", details_url="example.com"),
        )
        mock_get_commit_checks_result.return_value = (False, "test summary")

        # TODO: Remove after required status checks in GitHub have been switched to "Merge checks / Result"
        with self.assertRaises(SystemExit):
            run()

        mock_get_commit_checks_result.assert_called_once()
        self.assertEqual("pending", mock_set_commit_status.call_args_list[0].kwargs.get("state"))
        mock_get_commit_checks_result.assert_called_once()
        self.assertEqual("failure", mock_set_commit_status.call_args_list[1].kwargs.get("state"))
