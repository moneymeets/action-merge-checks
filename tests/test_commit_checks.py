import subprocess
from unittest import TestCase
from unittest.mock import MagicMock, patch

from merge_checks import commit_checks


@patch.object(commit_checks, "has_merge_commits")
@patch.object(commit_checks, "get_subject")
@patch.object(commit_checks, "fetch_full_history")
@patch.object(commit_checks, "get_base_revision")
@patch.object(commit_checks, "fetch_head_only")
class CommitChecksTest(TestCase):
    def test_happy_path(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        mock_get_base_revision.return_value = base_hash
        mock_get_subject.return_value = ("feat(component): subject",)
        mock_has_merge_commits.return_value = False

        self.assertEqual(True, commit_checks.get_commit_checks_result(head_hash=head_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_called_once()
        mock_get_subject.assert_called_once_with(head_hash, base_hash)
        mock_has_merge_commits.assert_called_once_with(head_hash, base_hash)

    def test_early_exit_no_commits(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        base_ref = "baseref"
        base_hash = "123abc"

        mock_get_base_revision.return_value = base_hash
        mock_has_merge_commits.return_value = False

        self.assertEqual(True, commit_checks.get_commit_checks_result(head_hash=base_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_not_called()
        mock_get_subject.assert_not_called()
        mock_has_merge_commits.assert_not_called()

    def test_fixup_found(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"
        mock_get_base_revision.return_value = base_hash
        mock_get_subject.return_value = ("feat(component):", "fixup!")
        mock_has_merge_commits.return_value = False

        self.assertEqual(False, commit_checks.get_commit_checks_result(head_hash=head_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_called_once()
        mock_get_subject.assert_called_once_with(head_hash, base_hash)
        mock_has_merge_commits.assert_not_called()

    def test_squash_found(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        mock_get_base_revision.return_value = base_hash
        mock_get_subject.return_value = ("feat(component):", "squash!")
        mock_has_merge_commits.return_value = False

        self.assertEqual(False, commit_checks.get_commit_checks_result(head_hash=head_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_called_once()
        mock_get_subject.assert_called_once_with(head_hash, base_hash)
        mock_has_merge_commits.assert_not_called()

    def test_merge_commit_found(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        mock_get_base_revision.return_value = base_hash
        mock_get_subject.return_value = ("feat(component):",)
        mock_has_merge_commits.return_value = True

        self.assertEqual(False, commit_checks.get_commit_checks_result(head_hash=head_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_called_once()
        mock_get_subject.assert_called_once_with(head_hash, base_hash)
        mock_has_merge_commits.assert_called_once_with(head_hash, base_hash)

    def test_has_wrong_commit_message(
        self,
        mock_fetch_head_only,
        mock_get_base_revision,
        mock_fetch_full_history,
        mock_get_subject,
        mock_has_merge_commits,
    ):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        mock_get_base_revision.return_value = base_hash
        mock_get_subject.return_value = ("chores(component): subject",)
        mock_has_merge_commits.return_value = False

        self.assertEqual(False, commit_checks.get_commit_checks_result(head_hash=head_hash, base_ref=base_ref)[0])
        mock_fetch_head_only.assert_called_once_with(base_ref)
        mock_get_base_revision.assert_called_once_with(base_ref)
        mock_fetch_full_history.assert_called_once()
        mock_get_subject.assert_called_once_with(head_hash, base_hash)
        mock_has_merge_commits.assert_called_once_with(head_hash, base_hash)


class ExternalCallTest(TestCase):
    @staticmethod
    def _mock_run_process(return_value: str):
        return patch.object(commit_checks, "_run_process", return_value=return_value)

    @patch.object(subprocess, "run", return_value=MagicMock(stdout="test-output       "))
    def test_run_process_call(self, mock_run):
        self.assertEqual(commit_checks._run_process("command"), "test-output")
        mock_run.assert_called_once_with(
            "command",
            check=True,
            shell=True,
            capture_output=True,
            text=True,
        )

    def test_has_merge_commits(self):
        with self._mock_run_process("parent_1") as mock_run_process:
            self.assertFalse(commit_checks.has_merge_commits("head", "base"))
            mock_run_process.assert_called_once()

        with self._mock_run_process("parent_1 parent_2") as mock_run_process:
            self.assertTrue(commit_checks.has_merge_commits("head", "base"))
            mock_run_process.assert_called_once()

    def test_get_subject(self):
        commits = ("feat(test): we test this", "fixup! feat(test): we test this")
        with self._mock_run_process("\n".join(commits)) as mock_run_process:
            self.assertEqual(commit_checks.get_subject("head", "base"), commits)
            mock_run_process.assert_called_once()

    def test_get_subject_markers(self):
        self.assertEqual(
            commit_checks.get_subject_markers(("feat(test): we test this", "fixup! feat(test): we test this")),
            ("feat(test):", "fixup!"),
        )

    def test_fetch_full_history(self):
        with self._mock_run_process("") as mock_run_process:
            commit_checks.fetch_full_history()
            mock_run_process.assert_called_once()

    def test_get_base_revision(self):
        with self._mock_run_process("base_ref") as mock_run_process:
            self.assertEqual(commit_checks.get_base_revision("base"), "base_ref")
            mock_run_process.assert_called_once()

    def test_fetch_head_only(self):
        with self._mock_run_process("") as mock_run_process:
            commit_checks.fetch_head_only("base")
            mock_run_process.assert_called_once()

    def test_has_wrong_commit_message(self):
        # Correct message
        self.assertEqual(commit_checks.has_wrong_commit_message(("chore(scope): test",)), ())
        self.assertEqual(
            commit_checks.has_wrong_commit_message(("feat(action): check commit message syntax and types",)),
            (),
        )

        # Incorrect message
        self.assertEqual(commit_checks.has_wrong_commit_message(("chores(scope): test",)), ("chores(scope): test",))
        self.assertEqual(commit_checks.has_wrong_commit_message(("chore(): test",)), ("chore(): test",))
        self.assertEqual(
            commit_checks.has_wrong_commit_message(("chores(scope1 scope2): test", "feat(scope): test")),
            ("chores(scope1 scope2): test",),
        )
        self.assertEqual(
            commit_checks.has_wrong_commit_message(("chore(scope):", "feat(scope):test")),
            ("chore(scope):", "feat(scope):test"),
        )
