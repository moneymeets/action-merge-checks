import logging
import re
from typing import Sequence

from github.Commit import Commit
from github.Repository import Repository

# https://github.com/moneymeets/moneymeets-docs/blob/master/_posts/2020-03-18-commit-message-branch-name-guidelines.md
ALLOWED_COMMIT_MESSAGE_TYPES = ("chore", "ci", "docs", "feat", "fix", "perf", "refactor", "style", "test")
LOGGING_PREFIX = "\n  "


def get_base_sha(repository: Repository) -> str:
    return repository.get_branch(repository.default_branch).commit.sha


def get_commits(repository: Repository, base_sha: str, head_hash: str) -> Sequence[Commit]:
    return tuple(repository.compare(base=base_sha, head=head_hash).commits)


def get_commit_messages(commits: Sequence[Commit]) -> Sequence[str]:
    logging.info("Getting commit messages...")
    return tuple(commit.commit.message for commit in commits)


def get_subject_markers(messages: Sequence[str]) -> Sequence[str]:
    logging.info("Getting subject markers...")
    return tuple(strip_allowed_markers(line).split(maxsplit=1)[0] for line in messages)


def has_merge_commits(commits: Sequence[Commit]) -> bool:
    logging.info("Checking for merge commits...")
    return any(len(parents) > 1 for parents in tuple(commit.parents for commit in commits))


def strip_allowed_markers(message: str) -> str:
    return message.removeprefix('Revert "').removesuffix('"')


def has_duplicated_commit_messages(messages: Sequence[str]) -> Sequence[str]:
    return tuple(set(message for message in messages if messages.count(message) > 1))


def has_wrong_commit_message(messages: Sequence[str]) -> Sequence[str]:
    return tuple(
        message
        for message in messages
        if re.match(rf"^({'|'.join(ALLOWED_COMMIT_MESSAGE_TYPES)})\([a-z\d-]+\): .+", strip_allowed_markers(message))
        is None
    )


def get_commit_checks_result(commits: Sequence[Commit]) -> tuple[bool, str]:
    messages = get_commit_messages(commits)
    logging.info(
        f"Found the following commit messages in branch:{LOGGING_PREFIX}{LOGGING_PREFIX.join(messages)}",
    )

    subject_markers = get_subject_markers(messages)

    fixups, squashes = (
        sum(1 for subject_marker in subject_markers if subject_marker == marker) for marker in ("fixup!", "squash!")
    )

    if fixups or squashes:
        return False, f"{fixups} fixup and {squashes} squash commits found"
    else:
        logging.info("No fixups or squashes found, check passed!")

    if has_merge_commits(commits):
        return False, "Contains merge commits"
    else:
        logging.info("Branch does not contain merge commits, check passed!")

    if duplicated_messages := has_duplicated_commit_messages(messages):
        logging.info(
            f"Found duplicated commit message(s): {LOGGING_PREFIX}{LOGGING_PREFIX.join(duplicated_messages)}",
        )
        return False, "Duplicated commit messages found"

    if incorrect_commit_messages := has_wrong_commit_message(messages):
        logging.info(
            f"Found invalid commit message(s): {LOGGING_PREFIX}{LOGGING_PREFIX.join(incorrect_commit_messages)}"
            f"\nAllowed types are: {ALLOWED_COMMIT_MESSAGE_TYPES}",
        )
        return False, "Invalid commit message format found"
    else:
        logging.info("Commit messages are correct, check passed!")

    return True, "All checks passed"
