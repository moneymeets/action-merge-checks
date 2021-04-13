# action-merge-checks

For example, use the following workflow in your repositories:

```yaml
name: Merge checks

on:
  push:
    branches:
      - feature/*

jobs:
  merge-checks:
    runs-on: ubuntu-20.04
    if: "!contains(github.event.head_commit.message, '[skip checks]')"
    steps:
      - uses: actions/checkout@v2

      - name: Merge checks
        uses: moneymeets/action-merge-checks@master
```

Here, `[skip checks]` in the commit message skips the check, returning `skipped` as the conclusion of the check run. 