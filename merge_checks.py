import os
import subprocess


def main(base_ref: str, head_ref: str):
    print(f"Checking out BASE_REF ({base_ref}) and HEAD_REF ({head_ref})...")

    subprocess.run(f"git fetch --depth=1 origin {base_ref}", check=True, shell=True)
    subprocess.run(f"git fetch origin {head_ref}", check=True, shell=True)

    base_revision = subprocess.run(f"git rev-parse origin/{base_ref}", check=True, shell=True, capture_output=True)
    head_revision = subprocess.run(f"git rev-parse origin/{head_ref}", check=True, shell=True, capture_output=True)

    base_hash, head_hash = (output.decode().strip() for output in (base_revision.stdout, head_revision.stdout))

    print("Getting commit list...")
    log = subprocess.run(f"git log --pretty='format:%H %s' {base_hash}..{head_hash}",
                         check=True, shell=True, capture_output=True)

    commits, subjects = zip(*(line.decode().split(maxsplit=1) for line in log.stdout.splitlines()))

    fixups, squashes = (
        len([subject for subject in subjects if marker in subject]) for marker in ("fixup!", "squash!")
    )

    if fixups or squashes:
        print(f"Found {fixups} fixup and {squashes} squash commits!")
        exit(1)
    else:
        print("No fixups or squashes found, check passed!")

    parents = subprocess.run(f"git log --pretty=%P {base_hash}..{head_hash}",
                             check=True, shell=True, capture_output=True)

    if any(len(line.split(maxsplit=1)) > 1 for line in parents.stdout.splitlines()):
        print("Branch contains merge commits!")
        exit(1)
    else:
        print("Branch does not contain merge commits, check passed!")

    print("All checks passed!")


if __name__ == "__main__":
    main(os.environ["BASE_REF"], os.environ["HEAD_REF"])
