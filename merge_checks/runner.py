import os
import sys
from dataclasses import asdict, dataclass
from enum import Enum

from .commit_checks import get_commit_checks_result
from .commit_status_setter import set_commit_status

BASE_REF = "master"


@dataclass
class Commit:
    repository: str
    commit_sha: str
    token: str


@dataclass
class Status:
    status_name: str
    details_url: str


class State(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


def get_commit_and_status() -> tuple[Commit, Status]:
    commit = Commit(
        repository=os.environ["GITHUB_REPOSITORY"],
        commit_sha=os.environ["GITHUB_SHA"],
        token=os.environ["GITHUB_TOKEN"],
    )

    status = Status(
        status_name="Merge checks / Result",
        details_url=f"{os.environ['GITHUB_SERVER_URL']}/{commit.repository}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
    )

    return commit, status


def run():
    commit, status = get_commit_and_status()

    set_commit_status(
        **(asdict(commit) | asdict(status)),
        state=State.PENDING.value,
        description="Merge checks running",
    )

    checks_passed, summary = get_commit_checks_result(head_hash=commit.commit_sha, base_ref=BASE_REF)

    set_commit_status(
        **(asdict(commit) | asdict(status)),
        state=(State.SUCCESS if checks_passed else State.FAILURE).value,
        description=summary,
    )

    # TODO: Remove after required status checks in GitHub have been switched to "Merge checks / Result"
    if not checks_passed:
        sys.exit(1)
