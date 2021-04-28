import os
import subprocess
import sys


def main(head_hash: str, base_ref: str) -> int:
    print(f"Checking out {base_ref}...")
    subprocess.run(f"git fetch --depth=1 origin {base_ref}", check=True, shell=True)
    base_revision = subprocess.run(f"git rev-parse origin/{base_ref}", check=True, shell=True, capture_output=True)

    base_hash = base_revision.stdout.decode().strip()

    if head_hash == base_hash:
        print(f"HEAD identical with {base_ref}, no commits to check")
        return 0

    print("Getting commit list...")
    subprocess.run("git fetch --unshallow", check=True, shell=True)
    log = subprocess.run(f"git log --pretty='format:%H %s' {base_hash}..{head_hash}",
                         check=True, shell=True, capture_output=True)

    commits, subjects = zip(*(line.decode().split(maxsplit=1) for line in log.stdout.splitlines()))

    fixups, squashes = (
        len([subject for subject in subjects if marker in subject]) for marker in ("fixup!", "squash!")
    )

    if fixups or squashes:
        print(f"Found {fixups} fixup and {squashes} squash commits!")
        return 1
    else:
        print("No fixups or squashes found, check passed!")

    parents = subprocess.run(f"git log --pretty=%P {base_hash}..{head_hash}",
                             check=True, shell=True, capture_output=True)

    if any(len(line.split(maxsplit=1)) > 1 for line in parents.stdout.splitlines()):
        print("Branch contains merge commits!")
        return 1
    else:
        print("Branch does not contain merge commits, check passed!")

    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main(head_hash=os.environ["GITHUB_SHA"], base_ref="master"))
