# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Pre-Plan Baseline Check

**Before starting any new plan or implementation task**, run unit tests and ruff to verify a clean baseline:

```bash
docker exec <container_name> python3 -m pytest /workspaces/gridenforcer_adapter/tests/ --tb=no -q
docker exec <container_name> ruff check /workspaces/gridenforcer_adapter/src/
```

The devcontainer name is typically `musing_leakey` (shared with gridenforcer_core). Verify with:
```bash
docker inspect <container_name> --format '{{range .Mounts}}{{.Source}}{{"\n"}}{{end}}' | grep gridenforcer_adapter
```

If there are any failing tests or ruff errors, **stop and inform the user** before proceeding. Do not start new work on top of a broken baseline.

## Definition of done

A feature is complete when:

1. The specified behavior works correctly across all described scenarios
2. Edge cases identified in the specification are handled
3. A corresponding unit test exists and passes
4. No linting errors are introduced
5. A oneline summary of the feature is added to CHANGELOG.md
6. README.md and PRD.md is updated to reflect the changes and user approved the updates
7. The changes are tested in the running install and explicitly approved by the user before committing and pushing
8. The associated Beads issue stays open until the user confirms the change works; only then close it
