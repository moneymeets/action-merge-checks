from unittest import TestCase
from unittest.mock import Mock

from merge_checks import commit_checks
from merge_checks.commit_checks import get_base_sha


class TestGetBaseSha(TestCase):
    def test_get_base_sha_returns_expected_sha(self):
        mock_repository = Mock()
        mock_repository.get_branch.return_value.commit.sha = "abc123"
        self.assertEqual("abc123", get_base_sha(mock_repository))


class TestGetCommitChecksResult(TestCase):
    def test_happy_path(self):
        mock_commit = Mock()
        mock_commit.commit.message = "feat(component): subject"
        mock_commit.parents = (Mock(),)

        self.assertEqual(
            (True, "All checks passed"),
            commit_checks.get_commit_checks_result(commits=(mock_commit,)),
        )

    def test_fixup_found(self):
        mock_commit = Mock()
        mock_commit.commit.message = "fixup! feat(component): subject"

        self.assertEqual(
            (False, "1 fixup and 0 squash commits found"),
            commit_checks.get_commit_checks_result(commits=(mock_commit,)),
        )

    def test_squash_found(self):
        mock_commit = Mock()
        mock_commit.commit.message = "squash! feat(component): subject"

        self.assertEqual(
            (False, "0 fixup and 1 squash commits found"),
            commit_checks.get_commit_checks_result(commits=(mock_commit,)),
        )

    #
    def test_merge_commit_found(self):
        mock_commit = Mock()
        mock_commit.commit.message = "feat(component): subject"
        mock_commit.parents = (Mock(), Mock())

        self.assertEqual(
            (False, "Contains merge commits"),
            commit_checks.get_commit_checks_result(commits=(mock_commit,)),
        )

    def test_has_wrong_commit_message(self):
        mock_commit = Mock()
        mock_commit.commit.message = "chores(component): subject"
        mock_commit.parents = (Mock(),)

        self.assertEqual(
            (False, "Invalid commit message format found"),
            commit_checks.get_commit_checks_result(commits=(mock_commit,)),
        )
