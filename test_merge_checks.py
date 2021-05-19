from unittest import TestCase
from unittest.mock import patch

import merge_checks


@patch.object(merge_checks, "has_merge_commits")
@patch.object(merge_checks, "get_subject_markers")
@patch.object(merge_checks, "fetch_full_history")
@patch.object(merge_checks, "get_base_revision")
@patch.object(merge_checks, "fetch_head_only")
class MergeCheckTest(TestCase):

    def test_happy_path(self, fetch_head_only, get_base_revision, fetch_full_history, get_subject_markers,
                        has_merge_commits):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        get_base_revision.return_value = base_hash
        get_subject_markers.return_value = ("feat(component):",)
        has_merge_commits.return_value = False

        self.assertEqual(0, merge_checks.main(head_hash=head_hash, base_ref=base_ref))
        fetch_head_only.assert_called_once_with(base_ref)
        get_base_revision.assert_called_once_with(base_ref)
        fetch_full_history.assert_called_once()
        get_subject_markers.assert_called_once_with(head_hash, base_hash)
        has_merge_commits.assert_called_once_with(head_hash, base_hash)

    def test_early_exit_no_commits(self, fetch_head_only, get_base_revision, fetch_full_history, get_subject_markers,
                                   has_merge_commits):
        base_ref = "baseref"
        base_hash = "123abc"

        get_base_revision.return_value = base_hash
        has_merge_commits.return_value = False

        self.assertEqual(0, merge_checks.main(head_hash=base_hash, base_ref=base_ref))
        fetch_head_only.assert_called_once_with(base_ref)
        get_base_revision.assert_called_once_with(base_ref)
        fetch_full_history.assert_not_called()
        get_subject_markers.assert_not_called()
        has_merge_commits.assert_not_called()

    def test_fixup_found(self, fetch_head_only, get_base_revision, fetch_full_history, get_subject_markers,
                         has_merge_commits):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"
        get_base_revision.return_value = base_hash
        get_subject_markers.return_value = ("feat(component):", "fixup!")
        has_merge_commits.return_value = False

        self.assertEqual(1, merge_checks.main(head_hash=head_hash, base_ref=base_ref))
        fetch_head_only.assert_called_once_with(base_ref)
        get_base_revision.assert_called_once_with(base_ref)
        fetch_full_history.assert_called_once()
        get_subject_markers.assert_called_once_with(head_hash, base_hash)
        has_merge_commits.assert_not_called()

    def test_squash_found(self, fetch_head_only, get_base_revision, fetch_full_history, get_subject_markers,
                          has_merge_commits):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        get_base_revision.return_value = base_hash
        get_subject_markers.return_value = ("feat(component):", "squash!")
        has_merge_commits.return_value = False

        self.assertEqual(1, merge_checks.main(head_hash=head_hash, base_ref=base_ref))
        fetch_head_only.assert_called_once_with(base_ref)
        get_base_revision.assert_called_once_with(base_ref)
        fetch_full_history.assert_called_once()
        get_subject_markers.assert_called_once_with(head_hash, base_hash)
        has_merge_commits.assert_not_called()

    def test_merge_commit_found(self, fetch_head_only, get_base_revision, fetch_full_history, get_subject_markers,
                                has_merge_commits):
        head_hash = "987xyz"
        base_ref = "baseref"
        base_hash = "123abc"

        get_base_revision.return_value = base_hash
        get_subject_markers.return_value = ("feat(component):",)
        has_merge_commits.return_value = True

        self.assertEqual(1, merge_checks.main(head_hash=head_hash, base_ref=base_ref))
        fetch_head_only.assert_called_once_with(base_ref)
        get_base_revision.assert_called_once_with(base_ref)
        fetch_full_history.assert_called_once()
        get_subject_markers.assert_called_once_with(head_hash, base_hash)
        has_merge_commits.assert_called_once_with(head_hash, base_hash)
