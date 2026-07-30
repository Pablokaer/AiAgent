#!/usr/bin/env bash
# PreToolUse hook for the Bash tool.
# Blocks `git commit` / `git push` unless the test suite passes.
# Hook contract (Claude Code): tool metadata arrives as JSON on stdin.
#   exit 0 -> allow;  exit 2 -> block (stderr is shown back to Claude).
# NOTE: confirm the exact stdin schema at https://code.claude.com/docs/en/hooks
set -euo pipefail

payload="$(cat)"

# Extract the command the Bash tool is about to run (jq if available, grep fallback).
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
else
  cmd="$(printf '%s' "$payload" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1)"
fi

# Only gate commits/pushes.
if printf '%s' "$cmd" | grep -qE 'git[[:space:]]+(commit|push)'; then
  if ! dotnet test --nologo -v q >/dev/null 2>&1; then
    echo "Blocked: run and pass 'dotnet test' before committing/pushing." >&2
    exit 2
  fi
fi

exit 0
