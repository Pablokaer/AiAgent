---
description: Fetch the NEXT ready issue from Linear and run the full loop on its target repo.
---

1. Run `python scripts/next_issue.py` from the orchestrator root. It prints a JSON object
   `{ "identifier": "...", "repo_url": "...", "title": "..." }` for the next ready issue,
   or the line `NONE`.
2. If it prints `NONE` (or no issue has a resolvable target repo), say there is nothing
   to do and stop.
3. Otherwise, carry out the `/work-issue` procedure for that `identifier`, passing the
   `repo_url` as the target repo.
