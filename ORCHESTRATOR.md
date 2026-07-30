# Central Orchestrator (Pattern B)

This repo (`AiAgent`) is the **brain**. It doesn't hold your product code — it holds
the AI loop (`.claude/`) and the automation that drives issues to merged PRs on
**other** repositories. Each Linear issue says which repo to work on.

## The self-moving cycle

```
Linear issue (team AID, label: ai-ready, description has "Target-Repo: <url>")
        │
        ▼
orchestrator-poll.yml   (cron every 15 min)
   · scripts/orchestrator_poll.py queries Linear for ai-ready issues
   · reads Target-Repo from each issue
   · dispatches orchestrator-work.yml (issue + repo_url)
   · swaps label ai-ready -> ai-working  (so it's not picked up twice)
        │
        ▼
orchestrator-work.yml
   · checks out THIS repo for the .claude loop config
   · clones the TARGET repo (auth via TARGET_REPOS_PAT)
   · injects .claude/ + CLAUDE.md into the target checkout
   · fetch_issue.py writes work/ISSUE.md (no MCP OAuth needed in CI)
   · claude -p runs /fix-and-test: coder -> test -> review, loop until green
   · commits, pushes a branch to the target repo, opens a PR "Fixes AID-123"
        │
        ▼
Target repo's own gates (dev -> integration -> stable -> main) run;
on merge to main the native GitHub<->Linear integration closes the issue.
If CI fails / PR rejected -> linear-on-review.yml opens a new issue -> back to poll.
```

The only recurring human input is **creating and prioritizing issues in Linear**.

## Issue convention (required for Pattern B)

Every issue the loop should pick up must:
1. Belong to team **AID**.
2. Carry the label **`ai-ready`**.
3. Contain a line in the description:
   ```
   Target-Repo: https://github.com/<owner>/<name>
   ```
   (If absent, the poller uses the first github.com URL it finds; if none, it skips.)

## One-time setup

**Secrets** (this repo → Settings → Secrets and variables → Actions):
| Secret | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Runs Claude in the worker |
| `LINEAR_API_KEY` | Poller + issue fetch |
| `TARGET_REPOS_PAT` | PAT with **Contents: write** + **Pull requests: write** on every target repo (and org-approved if they're org repos) |

> `GITHUB_TOKEN` is used by the poller to dispatch the worker — no secret needed for that.

**Linear labels**: create `ai-ready` and `ai-working` in team AID.

**Target repos**: for the promotion gates to apply, each target repo should carry the
same branch model (`dev`/`integration`/`stable`/`main`) and the CI workflows. If a
target has no `dev`, adjust the PR base or add the branches.

## Turning it on

1. Add the three secrets and the two labels.
2. Enable Actions on this repo (workflows run from `main`).
3. Create a Linear issue with the `ai-ready` label and a `Target-Repo:` line.
4. Wait for the cron (or run **orchestrator-poll** manually from the Actions tab).
   You can also run **orchestrator-work** manually, passing `issue` + `repo_url`.

## Upgrade to event-driven (optional)

Cron polling has up to ~15 min latency. To react instantly, add a Linear webhook that,
on issue label/state change, calls GitHub's `repository_dispatch` with event type
`work-linear-issue` and payload `{ "issue": "...", "repo_url": "..." }`. `orchestrator-work.yml`
already listens for that event. Because Linear webhooks can't call GitHub directly, put a
tiny relay (Cloudflare Worker / Azure Function) in between, or use a Linear automation/agent.
