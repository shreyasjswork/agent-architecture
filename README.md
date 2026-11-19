# Agent Architecture

A public reference for the workflow I use to maintain a multi-provider coding
setup. It covers how I route tasks, keep project context bounded, review an
exact revision, and decide when a change can ship.

The shared policies own workflow decisions. Provider adapters translate those
decisions into the commands each host supports. Project instructions keep
accounts, scope, and publication authority specific to the work. Daily health
checks measure the setup without invoking a model.

## Release boundary

1. Record the task, allowed paths, and acceptance checks.
2. Implement the change on an isolated branch and freeze the candidate commit.
3. Review that exact commit independently. Preserve the findings and the
   verification result.
4. Apply the manual or project-specific publication decision to that candidate.
5. Verify the actual merged or deployed result before closing the task.

Open [the architecture diagram](architecture.mmd) for the full flow.
The small [reference checker](scripts/check_release.py) verifies a frozen Git
range against the task scope and checks that the reviewer approved the same
candidate. It reads Git and reports a result. A passing result is evidence for
a release decision.

## Try the checker

Python 3.11 or later and Git are required. Copy
[the sample receipt](examples/release.json), fill in the two full commit hashes
from your local repository, and record the actual author, reviewer, and check
outcomes. Paths are relative to the Git root. Globs use case-sensitive shell
patterns, with `*` matching across directory separators.

```text
python scripts/check_release.py PATH_TO_WORKTREE PATH_TO_RECEIPT
python -m unittest discover -s tests
```

This edition contains the published architecture and an isolated example.
Workstation restore data, project-specific policies, account settings, and
provider snapshots belong to the private installation.
