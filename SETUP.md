# One-time setup

This repo is scaffolded. The steps below wire up the automation. Nothing here
contains secrets — you add those in GitHub.

## 1. GitHub Secrets & Variables
`Settings → Secrets and variables → Actions`

**Secrets**
| Name | Used by | Notes |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | claude.yml, claude-issue.yml | Claude API key |
| `LINEAR_API_KEY` | linear-on-review.yml | Linear personal API key |
| `GITHUB_MCP_PAT` | .mcp.json (local Claude) | GitHub PAT for the GitHub MCP server |
| `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID` | deploy-main.yml | Azure OIDC (configure later) |

**Variables**
| Name | Used by | Notes |
| --- | --- | --- |
| `LINEAR_TEAM_ID` | linear-on-review.yml | UUID of the Linear team |
| `AZURE_WEBAPP_NAME` | deploy-main.yml | App Service name (configure later) |

## 2. Linear
- The workspace currently has **one team: `Finperiti-ai`**. A team named **`AIdev`**
  does **not** exist yet and cannot be created through the connector — create or
  rename it in the Linear UI, then note its **team key** (the issue prefix).
- Replace the placeholder `AID` used in `CLAUDE.md` and `.claude/commands/fix-and-test.md`
  with your real team key so the magic word (`Fixes <KEY>-123`) closes issues on merge.
- Put the team **UUID** in the `LINEAR_TEAM_ID` Actions variable.
- Install the native GitHub ↔ Linear integration (Linear → Settings → Integrations → GitHub)
  so PRs/commits link to issues automatically.

## 3. Install the Claude GitHub App
Run once in interactive Claude Code from the repo:
```
/install-github-app
```

## 4. Branch protection (promotion gates)
`Settings → Branches → Add rule` for `dev`, `integration`, `stable`, `main`:
- Require a pull request before merging.
- Require status checks to pass (select the matching CI workflow per branch).
- Reviews: 1 for dev/integration, 2 for stable/main.
- For `main`, also protect against direct pushes.

## 5. GitHub Environment (deploy approval)
`Settings → Environments → New environment: production`
- Add required reviewers so the Azure deploy pauses for manual approval.

## 6. Azure (later)
Fill in `deploy-main.yml`: set `AZURE_WEBAPP_NAME` variable and the three
`AZURE_*` OIDC secrets. Configure a federated credential on an Azure AD app
registration scoped to this repo's `production` environment.

## 7. Push to GitHub
This folder is a fresh local repo. To publish:
```bash
git add -A
git commit -m "Scaffold Claude-driven .NET workflow"
git push -u origin main
# then create the promotion branches:
git push origin main:dev main:integration main:stable
```
