#!/usr/bin/env bash
# PostToolUse hook: auto-fix edited Python files with ruff (local uv venv).
# Silent on success; exits 2 with the remaining issues on stderr so Claude
# sees them next turn.
set -uo pipefail

input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
[[ -z "$file_path" || "$file_path" != *.py ]] && exit 0
[[ -n "${CLAUDE_PROJECT_DIR:-}" && "$file_path" != "$CLAUDE_PROJECT_DIR"/* ]] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
command -v uv >/dev/null 2>&1 || exit 0
[[ -d .venv ]] || exit 0

uv run ruff check --fix --silent "$file_path" >/dev/null 2>&1 || true
if ! output=$(uv run ruff check "$file_path" 2>&1); then
  echo "ruff found issues it could not auto-fix:" >&2
  echo "$output" | tail -20 >&2
  exit 2
fi
exit 0
