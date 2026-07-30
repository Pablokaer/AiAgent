#!/usr/bin/env python3
"""Return the NEXT ready Linear issue for the loop to work on.

Picks the highest-priority (then oldest) issue in the team that carries the
`ai-ready` label, is not already `ai-working`, and has a resolvable target repo
(a `Target-Repo:` line or a github.com URL in the description).

Prints a JSON object {identifier, repo_url, title, id} to stdout, or `NONE`.

Environment:
    LINEAR_API_KEY  required
    TEAM_KEY        default: AID
    READY_LABEL     default: ai-ready
    WORKING_LABEL   default: ai-working
"""
import json
import os
import re
import sys
import urllib.request

LINEAR_URL = "https://api.linear.app/graphql"


def linear(api_key, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        LINEAR_URL, data=body,
        headers={"Content-Type": "application/json", "Authorization": api_key},
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    if "errors" in data:
        sys.exit(f"Linear API error: {data['errors']}")
    return data["data"]


def extract_repo(description):
    if not description:
        return None
    m = re.search(r"Target-Repo:\s*(https://github\.com/[\w.-]+/[\w.-]+)", description, re.I)
    if not m:
        m = re.search(r"(https://github\.com/[\w.-]+/[\w.-]+)", description)
    return re.sub(r"\.git$", "", m.group(1).strip()) if m else None


def main():
    api_key = os.environ.get("LINEAR_API_KEY") or sys.exit("Missing LINEAR_API_KEY")
    team_key = os.environ.get("TEAM_KEY", "AID")
    ready = os.environ.get("READY_LABEL", "ai-ready")
    working = os.environ.get("WORKING_LABEL", "ai-working")

    data = linear(
        api_key,
        """query($key:String!,$ready:String!){
             issues(
               filter:{ team:{ key:{ eq:$key } }, labels:{ name:{ eq:$ready } } },
               first:50,
               orderBy: createdAt
             ){
               nodes{ id identifier title description priority createdAt
                      labels{ nodes{ name } } }
             }
           }""",
        {"key": team_key, "ready": ready},
    )["issues"]["nodes"]

    # Not already working; must have a resolvable target repo.
    candidates = []
    for it in data:
        names = {l["name"] for l in it["labels"]["nodes"]}
        if working in names:
            continue
        repo = extract_repo(it.get("description"))
        if not repo:
            continue
        candidates.append((it, repo))

    if not candidates:
        print("NONE")
        return

    # Linear priority: 1=urgent .. 4=low, 0=none. Sort urgent first, then oldest.
    def rank(pair):
        it = pair[0]
        pr = it.get("priority") or 0
        pr = pr if pr != 0 else 99  # no-priority last
        return (pr, it.get("createdAt") or "")

    it, repo = sorted(candidates, key=rank)[0]
    print(json.dumps({
        "identifier": it["identifier"],
        "repo_url": repo,
        "title": it["title"],
        "id": it["id"],
    }))


if __name__ == "__main__":
    main()
