# AiAgent — AI development loop orchestrator

The **brain** of a Claude-driven workflow. It pulls issues from Linear, runs a
write → test → review loop, and opens a PR on the **repository named in each issue**.
No product code lives here.

## The cycle

```
Linear issue (team AID, label: ai-ready, description: "Target-Repo: <url>")
        │
        ▼
poll (cron)  ──►  orchestrator-work.yml
                    · clone the target repo
                    · coder → test-runner → code-reviewer  (loop until green + APPROVED)
                    · commit → push branch → PR "Fixes AID-1"  (on the target repo)
        │
        ▼
merge on the target → Linear closes the issue
```

## Run it

**Autonomously (cloud):** the `orchestrator-poll.yml` cron picks up ready issues and
dispatches `orchestrator-work.yml`. Or trigger a single issue by hand:

```
gh workflow run orchestrator-work.yml --repo <owner>/AiAgent --ref main \
  -f issue=AID-1 -f repo_url=https://github.com/<owner>/<target>
```

**Locally (for testing):** open Claude Code in this repo and run:

```
/next-issue                 # next ready issue from Linear
# or
/work-issue AID-1 https://github.com/<owner>/<target>
```

See `ORCHESTRATOR.md` for the one-time setup (secrets, labels, issue convention).
