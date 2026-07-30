#!/usr/bin/env bash
# PostToolUse hook for Edit/Write. Applies a formatter if the stack has one.
# Never blocks (exit 0 even on failure).
if ls *.sln *.csproj >/dev/null 2>&1 || find . -maxdepth 2 -name '*.csproj' | grep -q . ; then
  dotnet format --no-restore >/dev/null 2>&1 || true
elif [ -f package.json ] && [ -x node_modules/.bin/prettier ]; then
  node_modules/.bin/prettier --write . >/dev/null 2>&1 || true
fi
exit 0
