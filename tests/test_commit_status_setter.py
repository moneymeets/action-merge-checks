from unittest.mock import patch

from merge_checks import commit_status_setter


@patch.object(commit_status_setter, "github")
def test_set_commit_status_calls_expected_functions(mock_github):
    commit_status_setter.set_commit_status(
        repository="test-repository",
        commit_sha="1234",
        token="xyz",
        status_name="test status",
        state="pending",
        description="test description",
        details_url="test.com",
    )
    mock_github.Github.assert_called_once_with(login_or_token="xyz")
    mock_github.Github.return_value.get_repo.assert_called_once_with("test-repository")
    mock_github.Github.return_value.get_repo.return_value.get_commit.assert_called_once_with(sha="1234")

    mock_commit = mock_github.Github.return_value.get_repo.return_value.get_commit.return_value
    mock_commit.create_status.assert_called_once_with(
        state="pending",
        target_url="test.com",
        description="test description",
        context="test status",
    )
