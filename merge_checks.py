import os
import subprocess
import sys
from typing import Tuple


def fetch_head_only(base_ref: str):
    print(f"Checking out {base_ref}...")
    subprocess.run(f"git fetch --depth=1 origin {base_ref}", check=True, shell=True)


def fetch_full_history():
    print("Getting commit list...")
    subprocess.run("git fetch --unshallow", check=True, shell=True)


def get_base_revision(base_ref: str) -> str:
    return subprocess.run(
        f"git rev-parse origin/{base_ref}",
        check=True,
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def get_subject_markers(head_hash: str, base_hash: str) -> Tuple[str, ...]:
    log = subprocess.run(
        f"git log --pretty='format:%s' {base_hash}..{head_hash}",
        check=True,
        shell=True,
        capture_output=True,
        text=True,
    )
    return tuple(line.split(maxsplit=1)[0] for line in log.stdout.splitlines())


def has_merge_commits(head_hash: str, base_hash: str) -> bool:
    parents = subprocess.run(
        f"git log --pretty=%p {base_hash}..{head_hash}",
        check=True,
        shell=True,
        capture_output=True,
        text=True,
    )
    return any(len(line.split(maxsplit=1)) > 1 for line in parents.stdout.splitlines())


def main(head_hash: str, base_ref: str) -> int:
    fetch_head_only(base_ref)
    base_hash = get_base_revision(base_ref)

    if head_hash == base_hash:
        print(f"HEAD identical with {base_ref}, no commits to check")
        return 0

    fetch_full_history()
    subject_markers = get_subject_markers(head_hash, base_hash)

    fixups, squashes = (
        sum(1 for subject_marker in subject_markers if subject_marker == marker) for marker in ("fixup!", "squash!")
    )

    if fixups or squashes:
        print(f"Found {fixups} fixup and {squashes} squash commits!")
        return 1
    else:
        print("No fixups or squashes found, check passed!")

    if has_merge_commits(head_hash, base_hash):
        print("Branch contains merge commits!")
        return 1
    else:
        print("Branch does not contain merge commits, check passed!")

    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main(head_hash=os.environ["GITHUB_SHA"], base_ref="master"))
