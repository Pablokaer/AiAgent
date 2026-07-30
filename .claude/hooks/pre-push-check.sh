#!/usr/bin/env bash
# PreToolUse hook for the Bash tool.
# Blocks `git commit` / `git push` unless the target project's checks pass.
# Stack is auto-detected from the current working directory.
#   exit 0 -> allow;  exit 2 -> block (stderr shown back to Claude).
# NOTE: confirm the stdin schema at https://code.claude.com/docs/en/hooks
set -uo pipefail

payload="$(cat)"
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
else
  cmd="$(printf '%s' "$payload" | grep -oE '"command"[^,]*' | head -1)"
fi

# Only gate commits/pushes.
printf '%s' "$cmd" | grep -qE 'git[[:space:]]+(commit|push)' || { echo '{"decision":"allow"}'; exit 0; }

run() { echo ">> $*" >&2; "$@" >/dev/null 2>&1; }

if ls *.sln *.csproj >/dev/null 2>&1 || find . -maxdepth 2 -name '*.csproj' | grep -q .; then
  run dotnet test --nologo -v q || { echo "Blocked: .NET tests must pass before commit/push." >&2; exit 2; }
elif [ -f package.json ]; then
  if grep -q '"test"' package.json; then
    run npm test || { echo "Blocked: npm test must pass before commit/push." >&2; exit 2; }
  fi
elif [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  if command -v pytest >/dev/null 2>&1; then
    run pytest -q || { echo "Blocked: pytest must pass before commit/push." >&2; exit 2; }
  fi
fi
# Static sites / unknown stacks: nothing to gate.
exit 0
