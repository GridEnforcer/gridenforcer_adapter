#!/usr/bin/env bash
# PreToolUse hook: force an explicit user confirmation on every `git push`.
# Definition of done: push only after the user has field-tested on the
# running HA install and explicitly approved (unit-green != field-green).
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

if printf '%s' "$cmd" | grep -qE '(^|[;&|[:space:]])git([[:space:]]+-[^[:space:]]+)*[[:space:]]+push'; then
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"DoD gate: git push requires field-green. Confirm the user has field-tested this change on the running HA install and explicitly approved. If not, cancel and deploy via the sync script instead."}}
EOF
fi
exit 0
