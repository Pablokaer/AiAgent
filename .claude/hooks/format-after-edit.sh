#!/usr/bin/env bash
# PostToolUse hook for Edit/Write.
# Applies formatting after edits. Never blocks (exit 0 even on failure).
# NOTE: confirm the exact hook schema at https://code.claude.com/docs/en/hooks
dotnet format --no-restore >/dev/null 2>&1 || true
exit 0
