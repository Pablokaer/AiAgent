#!/usr/bin/env python3
"""Central orchestrator poller (Pattern B).

Reads Linear for issues that are ready for the AI loop, extracts the target
GitHub repository from each issue, and dispatches the worker workflow that
runs /fix-and-test against that repo. Marks each dispatched issue so it is
not picked up again.

Issue convention: the issue description must contain a line:
    Target-Repo: https://github.com/<owner>/<name>
(otherwise the first github.com URL found in the description is used).

Environment:
    LINEAR_API_KEY   Linear personal API key (required)
    GH_TOKEN         GitHub token with actions:write on this repo (required)
    GH_REPO          owner/repo of THIS orchestrator repo (required)
    TEAM_KEY         Linear team key (default: AID)
    READY_LABEL      label that marks an issue as ready (default: ai-ready)
    WORKING_LABEL    label added once dispatched (default: ai-working)
    WORK_WORKFLOW    worker workflow file name (default: orchestrator-work.yml)
    DISPATCH_REF     git ref to dispatch on (default: main)
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

LINEAR_URL = "https://api.linear.app/graphql"


def env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        sys.exit(f"Missing required env var: {name}")
    return v


def linear(api_key, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        LINEAR_URL,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": api_key},
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    if "errors" in data:
        sys.exit(f"Linear API error: {data['errors']}")
    return data["data"]


def gh_dispatch(token, repo, workflow, ref, inputs):
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
    body = json.dumps({"ref": ref, "inputs": inputs}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status  # 204 == accepted
    except urllib.error.HTTPError as e:
        print(f"  ! dispatch failed: HTTP {e.code} {e.read().decode()}", file=sys.stderr)
        return e.code


def extract_repo(description):
    if not description:
        return None
    m = re.search(r"Target-Repo:\s*(https://github\.com/[\w.-]+/[\w.-]+)", description, re.I)
    if not m:
        m = re.search(r"(https://github\.com/[\w.-]+/[\w.-]+)", description)
    if not m:
        return None
    return re.sub(r"\.git$", "", m.group(1).strip())


def main():
    api_key = env("LINEAR_API_KEY", required=True)
    gh_token = env("GH_TOKEN", required=True)
    gh_repo = env("GH_REPO", required=True)
    team_key = env("TEAM_KEY", "AID")
    ready_label = env("READY_LABEL", "ai-ready")
    working_label = env("WORKING_LABEL", "ai-working")
    workflow = env("WORK_WORKFLOW", "orchestrator-work.yml")
    ref = env("DISPATCH_REF", "main")

    # Resolve label ids for the team.
    labels = linear(
        api_key,
        """query($key:String!){ teams(filter:{key:{eq:$key}}){ nodes{ id labels(first:250){ nodes{ id name } } } } }""",
        {"key": team_key},
    )
    teams = labels["teams"]["nodes"]
    if not teams:
        sys.exit(f"No Linear team with key '{team_key}'.")
    label_map = {l["name"]: l["id"] for l in teams[0]["labels"]["nodes"]}
    ready_id = label_map.get(ready_label)
    working_id = label_map.get(working_label)
    if not ready_id:
        sys.exit(f"Label '{ready_label}' not found in team {team_key}. Create it in Linear.")

    # Find ready issues that are not already working.
    issues = linear(
        api_key,
        """query($key:String!,$ready:ID!){
             issues(filter:{ team:{ key:{ eq:$key } }, labels:{ id:{ eq:$ready } } }, first:50){
               nodes{ id identifier title description url
                      labels{ nodes{ id name } } }
             }
           }""",
        {"key": team_key, "ready": ready_id},
    )["issues"]["nodes"]

    dispatched = 0
    for it in issues:
        names = {l["name"] for l in it["labels"]["nodes"]}
        if working_label in names:
            continue  # already in progress
        repo_url = extract_repo(it.get("description"))
        if not repo_url:
            print(f"- {it['identifier']}: no Target-Repo found, skipping.")
            continue

        print(f"- {it['identifier']} -> {repo_url} : dispatching worker")
        status = gh_dispatch(
            gh_token, gh_repo, workflow, ref,
            {"issue": it["identifier"], "repo_url": repo_url},
        )
        if status != 204:
            print(f"  ! not dispatched (HTTP {status}); leaving label untouched.")
            continue

        # Transition labels: drop ready, add working (best effort).
        if working_id:
            new_ids = [l["id"] for l in it["labels"]["nodes"] if l["id"] != ready_id]
            if working_id not in new_ids:
                new_ids.append(working_id)
            linear(
                api_key,
                """mutation($id:String!,$ids:[String!]){ issueUpdate(id:$id, input:{labelIds:$ids}){ success } }""",
                {"id": it["id"], "ids": new_ids},
            )
        dispatched += 1

    print(f"Done. Dispatched {dispatched} issue(s).")


if __name__ == "__main__":
    main()
