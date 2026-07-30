---
description: Fetch (and claim) the NEXT ready issue from Linear and run the full loop on its target repo.
---

1. Run `python scripts/next_issue.py` from the orchestrator root. It selects the next
   issue that is `ai-ready`, is NOT already `ai-working`, is NOT in a completed/canceled
   state, and has a resolvable target repo — then **claims** it (swaps the label
   `ai-ready` -> `ai-working`) so it is not picked again. It prints
   `{ "identifier": "...", "repo_url": "...", "title": "..." }`, or the line `NONE`.
   (Use `python scripts/next_issue.py --peek` to preview without claiming.)
2. If it prints `NONE`, say there is nothing to do and stop.
3. Otherwise, carry out the `/work-issue` procedure for that `identifier`, passing the
   `repo_url` as the target repo. The PR's `Fixes <id>` closes the issue on merge, which
   moves it to a completed state — so it is excluded from all future selections.
