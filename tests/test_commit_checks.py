from unittest import TestCase
from unittest.mock import Mock, patch

from merge_checks import commit_checks


@patch.object(commit_checks, "github")
@patch.object(commit_checks, "has_merge_commits")
@patch.object(commit_checks, "get_commit_messages")
class TestCommitChecks(TestCase):
    def test_happy_path(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        mock_get_commit_messages.return_value = ("feat(component): subject",)
        mock_has_merge_commits.return_value = False

        head_hash = Mock()
        self.assertEqual(
            (True, "All checks passed"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), head_hash),
        )
        repository = mock_github.Github.return_value.get_repo.return_value
        mock_get_commit_messages.assert_called_once_with(repository=repository, head_hash=head_hash)
        mock_has_merge_commits.assert_called_once_with(repository=repository, head_hash=head_hash)

    def test_early_exit_no_commits(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        head_hash = "abcdef"
        mock_github.Github.return_value.get_repo.return_value.get_branch.return_value.commit.sha = head_hash

        self.assertEqual(
            (True, "No commits to check"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), head_hash),
        )

        mock_get_commit_messages.assert_not_called()
        mock_has_merge_commits.assert_not_called()

    def test_fixup_found(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        mock_get_commit_messages.return_value = ("feat(component): subject", "fixup! feat(component): subject")
        mock_has_merge_commits.return_value = False

        self.assertEqual(
            (False, "1 fixup and 0 squash commits found"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), Mock()),
        )

    def test_squash_found(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        mock_get_commit_messages.return_value = ("feat(component): subject", "squash! feat(component): subject")
        mock_has_merge_commits.return_value = False

        self.assertEqual(
            (False, "0 fixup and 1 squash commits found"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), Mock()),
        )

    def test_merge_commit_found(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        mock_get_commit_messages.return_value = ("feat(component): subject",)
        mock_has_merge_commits.return_value = True

        self.assertEqual(
            (False, "Contains merge commits"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), Mock()),
        )

    def test_has_wrong_commit_message(self, mock_get_commit_messages, mock_has_merge_commits, mock_github):
        mock_get_commit_messages.return_value = ("chores(component): subject",)
        mock_has_merge_commits.return_value = False

        self.assertEqual(
            (False, "Invalid commit message format found"),
            commit_checks.get_commit_checks_result(Mock(), Mock(), Mock()),
        )
