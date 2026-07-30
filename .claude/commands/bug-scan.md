---
description: Scans the codebase for likely bugs and opens a Linear issue for the most important one
argument-hint: [optional area or path to focus on]
---

Focus area (optional): $ARGUMENTS

1. Build and run the tests to confirm the current baseline.
2. Scan the code for likely bugs, security risks, and correctness issues
   (null handling, error paths, async misuse, input validation, resource leaks).
   Prefer high-impact, well-evidenced findings over stylistic nits.
3. Pick the single most important issue. If nothing material is found, say so and stop.
4. Create a Linear issue via MCP in the configured team with:
   - a clear title,
   - a description including file:line references and a proposed fix,
   - acceptance criteria.
5. Report the created issue id so it can be handed to `/fix-and-test`.
