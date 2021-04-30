from unittest import TestCase
from unittest.mock import patch

import merge_checks


def patch_fetch_head_only():
    return patch.object(merge_checks, "fetch_head_only")


def patch_get_base_revision(result: str):
    return patch.object(merge_checks, "get_base_revision", return_value=result)


def patch_fetch_full_history():
    return patch.object(merge_checks, "fetch_full_history")


def patch_get_subject_markers(*markers: str):
    return patch.object(merge_checks, "get_subject_markers", return_value=tuple(markers))


def patch_has_merge_commits(result: bool):
    return patch.object(merge_checks, "has_merge_commits", return_value=result)


class MergeCheckTest(TestCase):
    def test_happy_path(self):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        with patch_fetch_head_only() as fetch_head_only_mock, \
                patch_get_base_revision(base_hash) as get_base_revision_mock, \
                patch_fetch_full_history() as fetch_full_history_mock, \
                patch_get_subject_markers("firstsubjectword") as get_subject_markers_mock, \
                patch_has_merge_commits(False) as has_merge_commits_mock:
            self.assertEqual(0, merge_checks.main(head_hash, base_ref))
            fetch_head_only_mock.assert_called_once_with(base_ref)
            get_base_revision_mock.assert_called_once_with(base_ref)
            fetch_full_history_mock.assert_called_once()
            get_subject_markers_mock.assert_called_once_with(head_hash, base_hash)
            has_merge_commits_mock.assert_called_once_with(head_hash, base_hash)

    def test_early_exit_no_commits(self):
        base_ref = "baseref"
        base_hash = "123abc"

        with patch_fetch_head_only() as fetch_head_only_mock, \
                patch_get_base_revision(base_hash) as get_base_revision_mock, \
                patch_fetch_full_history() as fetch_full_history_mock, \
                patch_get_subject_markers() as get_subject_markers_mock, \
                patch_has_merge_commits(False) as has_merge_commits_mock:
            self.assertEqual(0, merge_checks.main(base_hash, base_ref))
            fetch_head_only_mock.assert_called_once_with(base_ref)
            get_base_revision_mock.assert_called_once_with(base_ref)
            fetch_full_history_mock.assert_not_called()
            get_subject_markers_mock.assert_not_called()
            has_merge_commits_mock.assert_not_called()

    def test_fixup_squash_found(self):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        for marker in ("fixup!", "squash!"):
            with patch_fetch_head_only() as fetch_head_only_mock, \
                    patch_get_base_revision(base_hash) as get_base_revision_mock, \
                    patch_fetch_full_history() as fetch_full_history_mock, \
                    patch_get_subject_markers("feat(component):", marker) as get_subject_markers_mock, \
                    patch_has_merge_commits(False) as has_merge_commits_mock:
                self.assertEqual(1, merge_checks.main(head_hash, base_ref))
                fetch_head_only_mock.assert_called_once_with(base_ref)
                get_base_revision_mock.assert_called_once_with(base_ref)
                fetch_full_history_mock.assert_called_once()
                get_subject_markers_mock.assert_called_once_with(head_hash, base_hash)
                has_merge_commits_mock.assert_not_called()

    def test_merge_commit_found(self):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        with patch_fetch_head_only() as fetch_head_only_mock, \
                patch_get_base_revision(base_hash) as get_base_revision_mock, \
                patch_fetch_full_history() as fetch_full_history_mock, \
                patch_get_subject_markers("feat(component):") as get_subject_markers_mock, \
                patch_has_merge_commits(True) as has_merge_commits_mock:
            self.assertEqual(1, merge_checks.main(head_hash, base_ref))
            fetch_head_only_mock.assert_called_once_with(base_ref)
            get_base_revision_mock.assert_called_once_with(base_ref)
            fetch_full_history_mock.assert_called_once()
            get_subject_markers_mock.assert_called_once_with(head_hash, base_hash)
            has_merge_commits_mock.assert_called_once_with(head_hash, base_hash)
