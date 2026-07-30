# Project: AIFinperiti

AI-driven development workflow repository. Claude Code writes → reviews → tests → ships
C#/.NET code through branch-based promotion gates, tracked in Linear and deployed to Azure.

## Stack

- .NET 10 (LTS) / C# (latest)
- ASP.NET Core Web API — `AIFinperiti.Api`
- Testing: xUnit + Moq — `AIFinperiti.Api.Tests`
- EF Core (add when persistence is introduced)

## Layout

```
AIFinperiti.sln
Directory.Build.props        # shared build settings (net10.0, nullable, warnings-as-errors)
src/
  AIFinperiti.Api/           # Web API
  AIFinperiti.Api.Tests/     # xUnit tests
```

## Commands

| Command | Purpose |
| --- | --- |
| `dotnet build` | Compile the solution |
| `dotnet test` | Run all tests |
| `dotnet format` | Apply formatting/style fixes |
| `dotnet format --verify-no-changes` | Fail if formatting is needed (used in CI) |

## Rules before committing

1. All tests pass (`dotnet test`).
2. `dotnet format` applied — zero analyzer warnings (build treats warnings as errors).
3. Coverage must not drop.
4. Smallest possible diff for the requested change.

## Conventions

- `PascalCase` for public members, `_camelCase` for private fields.
- XML docs on all public API surface.
- One type per file; namespace matches folder path.
- Prefer constructor injection; register services in `Program.cs`.

## Branch flow (promotion gates)

`dev` (fast) → `integration` (medium) → `stable` (slow) → `main` (deploy to Azure).

Work on a Linear issue happens on a dedicated branch (see below), which is PR'd into `dev`.

## Working an issue

Each Linear issue gets its own working branch, named `<team-key>-<number>-<slug>`
(e.g. `aid-123-fix-health-endpoint`). Use the `/fix-and-test` command to drive the
cycle. Reference the issue in the PR body with a magic word so it closes on merge:
`Fixes AID-123`.

> The Linear magic-word prefix must match the real team key. See `SETUP.md`.
