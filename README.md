# action-merge-checks

For example, use the following workflow in your repositories:

```yaml
name: Merge checks

on:
  pull_request_target:

jobs:
  merge-checks:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name != github.repository && !contains(github.event.pull_request.head_commit.message, '[skip checks]')
    steps:
      - uses: actions/checkout@v4

      - name: Merge checks
        uses: midnightcommander/action-merge-checks@master
```

Here, `[skip checks]` in the commit message skips the check, returning `skipped` as the conclusion of the check run.
