# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development setup

Local `uv` venv (no devcontainer):

```bash
uv venv
uv pip install -e ".[dev]"
```

`.python-version` pins to 3.12 so `uv venv` picks the right interpreter automatically.

## Pre-Plan Baseline Check

**Before starting any new plan or implementation task**, run unit tests and ruff to verify a clean baseline:

```bash
uv run pytest tests/ --tb=no -q
uv run ruff check src/
```

If there are any failing tests or ruff errors, **stop and inform the user** before proceeding. Do not start new work on top of a broken baseline.

Beads (issue tracking) live in the sibling repo `gridenforcer_planning` — clone it next to this repo and run `bd ready` / `bd create` / etc. from there. Bead IDs use the `ge-` prefix; historical CHANGELOG entries referencing `gridenforcer_core-<id>` map 1:1 to `ge-<id>`.

## Branching

When claiming a bead, create a feature branch off `main` (e.g. `bd-<id>/<short-slug>`) and do all work there. Merge to `main` via PR after field-green. Direct pushes to `main` are blocked by GitHub branch protection.

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
