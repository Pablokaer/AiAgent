---
description: Implements a Linear/GitHub issue (or free-text task) and iterates until tests pass, then opens a PR
argument-hint: <issue-id | #github-number | free description>
---

Task source: $ARGUMENTS

0. Resolve the task source:
   - If it looks like a Linear issue ID (e.g. AID-123), fetch the full issue from
     Linear via MCP: title, description, acceptance criteria, comments.
   - If it looks like a GitHub issue (#42), fetch it from GitHub via MCP.
   - Otherwise, treat $ARGUMENTS as the task description itself.
   Restate the requirement in one sentence before starting.

1. Create a working branch off `dev` named `<team-key>-<number>-<slug>`
   (e.g. `aid-123-fix-health-endpoint`). If there is no issue number, use a short slug.

2. Use the `dotnet-coder` subagent to implement the change (smallest diff).

3. Use the `test-runner` subagent to run the tests.

4. If there are failures, go back to `dotnet-coder` to fix them. Repeat 2–3 until `TESTS GREEN`.

5. Use the `code-reviewer` subagent. If it does not return `APPROVED`, fix and repeat from step 3.

6. Ensure `dotnet format --verify-no-changes` passes.

7. Commit with a clear message and open a PR into `dev`. Put `Fixes AID-123` in the PR
   body (use the real issue id) so the Linear issue closes on merge to `main`.
