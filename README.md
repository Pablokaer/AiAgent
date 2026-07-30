# employees-pablo3 (AIFinperiti)

Claude-driven development workflow: an AI loop that **writes → reviews → tests → ships**
C#/.NET code through branch-based promotion gates, tracked in Linear and deployed to Azure.

## Branch flow

```
dev ──(fast)──► integration ──(medium)──► stable ──(slow)──► main ──► Azure
```

- **dev** — build, format check, unit tests
- **integration** — + integration tests
- **stable** — + full suite + dependency vulnerability scan
- **main** — deploy to Azure App Service (with environment approval)

Each Linear issue is worked on its own branch and merged via `Fixes AID-123`.

## Quick start

```bash
dotnet restore
dotnet build
dotnet test
dotnet run --project src/AIFinperiti.Api   # GET /health -> "OK"
```

## AI loop

- `.claude/agents/` — `dotnet-coder`, `code-reviewer`, `test-runner`
- `.claude/commands/fix-and-test.md` — orchestrates the loop for an issue
- `.claude/commands/bug-scan.md` — finds a bug and opens a Linear issue
- `.claude/hooks/` — block commit/push without passing tests; auto-format after edits

See **SETUP.md** for the one-time configuration (secrets, Linear team, Azure, branch protection).
