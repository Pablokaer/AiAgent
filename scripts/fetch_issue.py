#!/usr/bin/env python3
"""Fetch a Linear issue by identifier and write it to a Markdown file.

Used by the worker workflow so the headless loop does not need the Linear MCP
(which requires interactive OAuth) inside CI.

Environment:
    LINEAR_API_KEY  Linear personal API key (required)
    ISSUE           issue identifier, e.g. AID-123 (required)
    OUT             output path (default: ISSUE.md)
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


def main():
    api_key = os.environ.get("LINEAR_API_KEY") or sys.exit("Missing LINEAR_API_KEY")
    ident = os.environ.get("ISSUE") or sys.exit("Missing ISSUE")
    out = os.environ.get("OUT", "ISSUE.md")

    m = re.match(r"([A-Za-z]+)-(\d+)$", ident.strip())
    if not m:
        sys.exit(f"ISSUE '{ident}' is not a valid identifier like AID-123")
    key, number = m.group(1).upper(), int(m.group(2))

    data = linear(
        api_key,
        """query($key:String!,$num:Float!){
             issues(filter:{ team:{ key:{ eq:$key } }, number:{ eq:$num } }, first:1){
               nodes{ identifier title description url }
             }
           }""",
        {"key": key, "num": number},
    )
    nodes = data["issues"]["nodes"]
    if not nodes:
        sys.exit(f"Issue {ident} not found.")
    it = nodes[0]

    with open(out, "w") as f:
        f.write(f"# {it['identifier']}: {it['title']}\n\n")
        f.write(f"Linear: {it['url']}\n\n")
        f.write("## Description\n\n")
        f.write((it.get("description") or "_(no description)_") + "\n")
    print(f"Wrote {out} for {it['identifier']}: {it['title']}")


if __name__ == "__main__":
    main()
