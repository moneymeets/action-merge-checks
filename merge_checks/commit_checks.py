import logging
import re
from typing import Sequence

import github
from github.Commit import Commit
from github.Repository import Repository

# https://github.com/moneymeets/moneymeets-docs/blob/master/_posts/2020-03-18-commit-message-branch-name-guidelines.md
ALLOWED_COMMIT_MESSAGE_TYPES = ("chore", "ci", "docs", "feat", "fix", "perf", "refactor", "style", "test")
LOGGING_PREFIX = "\n  "


def get_commits(repository: Repository, head_hash: str) -> Sequence[Commit]:
    return tuple(set(repository.get_commits(head_hash)) - set(repository.get_commits(repository.default_branch)))


def get_commit_messages(repository: Repository, head_hash: str) -> Sequence[str]:
    logging.info("Getting commit messages...")
    return tuple(commit.commit.message for commit in get_commits(repository=repository, head_hash=head_hash))


def get_subject_markers(subjects: Sequence[str]) -> Sequence[str]:
    logging.info("Getting subject markers...")
    return tuple(line.split(maxsplit=1)[0] for line in subjects)


def has_merge_commits(repository: Repository, head_hash: str) -> bool:
    logging.info("Checking for merge commits...")
    return any(
        len(parents) > 1
        for parents in tuple(commit.parents for commit in get_commits(repository=repository, head_hash=head_hash))
    )


def has_wrong_commit_message(subject_markers: Sequence[str]) -> Sequence[str]:
    return tuple(
        marker
        for marker in subject_markers
        if re.match(rf"^({'|'.join(ALLOWED_COMMIT_MESSAGE_TYPES)})\([a-z\d-]+\): .+", marker) is None
    )


def get_commit_checks_result(repository_name: str, github_token: str, head_hash: str) -> tuple[bool, str]:

    repository = github.Github(login_or_token=github_token).get_repo(repository_name)

    if head_hash == repository.get_branch(repository.default_branch).commit.sha:
        logging.warning(f"HEAD identical with {repository.default_branch}, no commits to check")
        return True, "No commits to check"

    subjects = get_commit_messages(repository=repository, head_hash=head_hash)
    logging.info(
        f"Found the following commit messages in branch:{LOGGING_PREFIX}{LOGGING_PREFIX.join(subjects)}",
    )

    subject_markers = get_subject_markers(subjects)

    fixups, squashes = (
        sum(1 for subject_marker in subject_markers if subject_marker == marker) for marker in ("fixup!", "squash!")
    )

    if fixups or squashes:
        return False, f"{fixups} fixup and {squashes} squash commits found"
    else:
        logging.info("No fixups or squashes found, check passed!")

    if has_merge_commits(repository=repository, head_hash=head_hash):
        return False, "Contains merge commits"
    else:
        logging.info("Branch does not contain merge commits, check passed!")

    if incorrect_commit_messages := has_wrong_commit_message(subjects):
        logging.info(
            f"Found invalid commit message(s): {LOGGING_PREFIX}{LOGGING_PREFIX.join(incorrect_commit_messages)}"
            f"\nAllowed types are: {ALLOWED_COMMIT_MESSAGE_TYPES}",
        )
        return False, "Invalid commit message format found"
    else:
        logging.info("Commit messages are correct, check passed!")

    return True, "All checks passed"
