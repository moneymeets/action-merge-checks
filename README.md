# action-merge-checks

```yaml
name: Merge checks

on:
  pull_request:
    types: [synchronize]

jobs:
  merge-checks:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Merge checks
        uses: moneymeets/action-merge-checks
```
