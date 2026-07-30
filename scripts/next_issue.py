#!/usr/bin/env python3
"""Return (and claim) the NEXT ready Linear issue for the loop to work on.

Selection rules (so resolved / in-progress issues are never re-picked):
- team == TEAM_KEY and has label READY_LABEL (ai-ready)
- NOT already labelled WORKING_LABEL (ai-working)  -> not in progress
- state type is not "completed" or "canceled"       -> not already resolved
- description has a resolvable Target-Repo

By default the chosen issue is CLAIMED: its label is swapped ai-ready -> ai-working,
so a second run of /next-issue (or the cron poller) will not pick it again. Pass
`--peek` to inspect without claiming.

Prints JSON {identifier, repo_url, title, id} or the line `NONE`.

Env: LINEAR_API_KEY (required), TEAM_KEY=AID, READY_LABEL=ai-ready, WORKING_LABEL=ai-working
"""
import json
import os
import re
import sys
import urllib.request

LINEAR_URL = "https://api.linear.app/graphql"
CLOSED_STATES = {"completed", "canceled"}


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
    peek = "--peek" in sys.argv
    api_key = os.environ.get("LINEAR_API_KEY") or sys.exit("Missing LINEAR_API_KEY")
    team_key = os.environ.get("TEAM_KEY", "AID")
    ready = os.environ.get("READY_LABEL", "ai-ready")
    working = os.environ.get("WORKING_LABEL", "ai-working")

    data = linear(
        api_key,
        """query($key:String!,$ready:String!){
             issues(
               filter:{ team:{ key:{ eq:$key } }, labels:{ name:{ eq:$ready } } },
               first:50, orderBy: createdAt
             ){
               nodes{ id identifier title description priority createdAt
                      state{ type }
                      labels{ nodes{ id name } } }
             }
           }""",
        {"key": team_key, "ready": ready},
    )["issues"]["nodes"]

    candidates = []
    for it in data:
        names = {l["name"] for l in it["labels"]["nodes"]}
        if working in names:
            continue  # already in progress
        if (it.get("state") or {}).get("type") in CLOSED_STATES:
            continue  # already resolved / canceled
        repo = extract_repo(it.get("description"))
        if not repo:
            continue
        candidates.append((it, repo))

    if not candidates:
        print("NONE")
        return

    def rank(pair):
        it = pair[0]
        pr = it.get("priority") or 0
        pr = pr if pr != 0 else 99   # no-priority sorts last
        return (pr, it.get("createdAt") or "")

    it, repo = sorted(candidates, key=rank)[0]

    if not peek:
        # Claim it: resolve label ids, swap ai-ready -> ai-working.
        team = linear(
            api_key,
            """query($key:String!){ teams(filter:{key:{eq:$key}}){ nodes{ labels(first:250){ nodes{ id name } } } } }""",
            {"key": team_key},
        )["teams"]["nodes"]
        label_ids = {l["name"]: l["id"] for l in team[0]["labels"]["nodes"]} if team else {}
        working_id = label_ids.get(working)
        ready_id = label_ids.get(ready)
        if working_id:
            new_ids = [l["id"] for l in it["labels"]["nodes"] if l["id"] != ready_id]
            if working_id not in new_ids:
                new_ids.append(working_id)
            linear(
                api_key,
                """mutation($id:String!,$ids:[String!]){ issueUpdate(id:$id, input:{labelIds:$ids}){ success } }""",
                {"id": it["id"], "ids": new_ids},
            )

    print(json.dumps({
        "identifier": it["identifier"],
        "repo_url": repo,
        "title": it["title"],
        "id": it["id"],
    }))


if __name__ == "__main__":
    main()
