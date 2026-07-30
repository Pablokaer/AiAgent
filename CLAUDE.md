# Orchestrator (AI development loop)

This repository is **only the brain**. It contains no product code. Its job is to
fetch the next ready issue from Linear, run an AI loop that implements what the issue
describes, and deliver the result (a PR, or a direct push) to the **target repository
named in that issue**.

## How it works

1. An issue lives in Linear (team **AID**), labelled **`ai-ready`**, and its description
   contains a line `Target-Repo: https://github.com/<owner>/<name>`.
2. The loop clones that target repo, detects its stack, implements the change, runs the
   project's checks until green, reviews, and opens a PR with `Fixes AID-<n>` (or pushes
   directly if the issue asks for it).
3. This repo never receives the product changes — only the target repo does.

## Commands

- `/next-issue` — fetch the next ready issue from Linear and run the loop on its target.
- `/work-issue <id> [repo-url]` — run the loop for a specific issue against its repo.

## Subagents (stack-agnostic)

- `coder` — detects the stack (.NET / Node / Python / static HTML) and implements the issue.
- `test-runner` — runs the project's tests/checks (or a well-formedness check for static sites).
- `code-reviewer` — reviews the diff against the acceptance criteria; must say `APPROVED`.

## Issue convention

- Team **AID**, label **`ai-ready`** (swapped to `ai-working` once picked up).
- A `Target-Repo:` line (or a github.com URL) in the description.
- The loop closes the issue via the magic word `Fixes AID-<n>` on merge to the target's default branch.

## Notes

- The loop runs where `claude` starts (this repo, so `.claude/` loads); it clones the
  target into `./work` and operates there.
- The target repo must be one where the configured token has write access.
