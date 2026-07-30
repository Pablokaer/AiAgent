---
description: Clone the repo named in an issue, implement the issue with the loop, and open a PR (or direct push) to THAT repo.
argument-hint: <issue-id> [target-repo-url]
---

Work the issue **$ARGUMENTS** end to end, against ITS OWN repository. This repo is only
the orchestrator — the code changes must land in the target repo named by the issue.

0. Resolve the task:
   - If `./ISSUE.md` exists (CI), use it as the issue source. Otherwise fetch the issue
     from Linear via the connector using the id (e.g. AID-1): title, description,
     acceptance criteria.
   - Determine the TARGET REPO: the second argument if given, else a line
     `Target-Repo: <url>` in the description, else the first github.com URL found.
     If none can be found, STOP and report that the issue has no target repo.
   - Restate, in one sentence: the requirement + the target repo + whether the issue
     asks for a direct push or a PR (default: PR).

1. Clone the target repo into `./work` and `cd ./work`:
   `git clone https://github.com/<owner>/<name>.git work` (auth is already configured).
   - If the repo is empty (no commits), initialize it and work on the default branch.
   - Otherwise create a branch `<key>-<number>-<slug>` off `dev` if it exists, else off
     the default branch.

2. Use the `coder` subagent to implement the requirement (it detects the stack).
3. Use the `test-runner` subagent. On failure, return to `coder`. Repeat until
   `TESTS GREEN` (or `NO TESTS (static)` for a static change).
4. Use the `code-reviewer` subagent. If not `APPROVED`, fix and repeat from step 3.
5. Commit. Then:
   - PR mode (default): push the branch to origin and open a PR into the base branch
     with `Fixes <issue-id>` in the body (`gh pr create`).
   - Direct-push mode (only if the issue explicitly requests it): push straight to the
     default branch.
6. Report: target repo, branch, and the PR url or pushed commit sha.
