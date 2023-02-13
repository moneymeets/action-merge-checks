import github


def set_commit_status(
    repository: str,
    commit_sha: str,
    token: str,
    status_name: str,
    state: str,
    description: str,
    details_url: str,
):
    github.Github(login_or_token=token).get_repo(repository).get_commit(sha=commit_sha).create_status(
        state=state,
        target_url=details_url,
        description=description,
        context=status_name,
    )
