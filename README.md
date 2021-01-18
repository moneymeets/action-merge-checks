# action-merge-checks

```yaml
name: Merge checks

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  merge-checks:
    runs-on: ubuntu-20.04

    steps:
      - uses: actions/checkout@v2

      - name: Merge checks
        uses: moneymeets/action-merge-checks@master
```
