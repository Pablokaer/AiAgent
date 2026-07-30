# Orchestrator setup & operation

`AiAgent` is the brain. It never holds product code — it drives issues to PRs on
**other** repositories, one per issue.

## The self-moving cycle

```
Linear issue (team AID, label: ai-ready, description: "Target-Repo: <url>")
        │
        ▼
orchestrator-poll.yml   (cron every 15 min)
   · orchestrator_poll.py finds ai-ready issues (not ai-working)
   · reads Target-Repo, dispatches orchestrator-work.yml (issue + repo_url)
   · swaps label ai-ready -> ai-working
        │
        ▼
orchestrator-work.yml
   · checks out THIS repo (loads .claude + scripts)
   · fetch_issue.py writes ISSUE.md
   · claude -p "/work-issue <id> <repo_url>"
        - clones the TARGET repo into ./work
        - coder (detects stack) -> test-runner -> code-reviewer, loop until green + APPROVED
        - commit, push branch to the target, open PR "Fixes AID-<n>"
        │
        ▼
merge on the target repo -> GitHub<->Linear closes the issue.
```

Only recurring human input: **create & prioritize issues in Linear**.

## Issue convention (required)

Each issue the loop should pick up must:
1. Belong to team **AID**.
2. Carry the label **`ai-ready`**.
3. Contain in its description:
   ```
   Target-Repo: https://github.com/<owner>/<name>
   ```
   (Otherwise the first github.com URL is used; if none, the issue is skipped.)
4. Optionally state "commit directly" if you want a direct push instead of a PR.

## Stack-agnostic loop

The subagents detect the target's stack and act accordingly:
- `.sln`/`.csproj` → .NET (`dotnet build`/`test`/`format`)
- `package.json` → Node (`npm test` / build)
- `pyproject.toml`/`requirements.txt` → Python (`pytest`)
- only static `*.html` → no build; HTML well-formedness check
The worker image has .NET 10, Node 20 and Python 3.12 preinstalled; extend it for other stacks.

## One-time setup

**Secrets** (this repo → Settings → Secrets and variables → Actions):
| Secret | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Runs Claude in the worker |
| `LINEAR_API_KEY` | Poll + issue fetch |
| `TARGET_REPOS_PAT` | PAT with **Contents: write** + **Pull requests: write** on every target repo (org-approved if they're org repos) |

`GITHUB_TOKEN` (automatic) lets the poller dispatch the worker — no secret needed.

**Linear labels**: create `ai-ready` and `ai-working` in team AID.

**Enable Actions** on this repo (workflows run from `main`).

## Running it

- **Autonomous:** just create `ai-ready` issues with a `Target-Repo:` line. The cron
  (or a manual run of **orchestrator-poll**) does the rest.
- **One issue by hand (cloud):**
  ```
  gh workflow run orchestrator-work.yml --repo <owner>/AiAgent --ref main \
    -f issue=AID-1 -f repo_url=https://github.com/<owner>/<target>
  ```
- **Locally (testing):** open Claude Code in this repo and run `/next-issue`
  or `/work-issue AID-1 <repo-url>`. Needs `gh` authenticated and the Linear MCP connected.

## Upgrade to event-driven (optional)

To react instantly instead of polling, add a Linear webhook that calls GitHub's
`repository_dispatch` with type `work-linear-issue` and payload `{issue, repo_url}`.
`orchestrator-work.yml` already listens for it. Linear can't call GitHub directly, so put
a tiny relay (Cloudflare Worker / Azure Function) in between.
