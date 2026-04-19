---
name: coolify-one-click-deploy
description: >
  Forks an open-source GitHub repo and deploys it to Coolify via Docker Compose,
  auto-wiring all env vars. Two modes: (1) opensaasapps — public fork, no rebrand,
  upstream credit as-is, OSI licenses only; (2) unboxd.cloud — private fork,
  full rebrand (new name, compose service names patched, LICENSE updated), upstream
  credit always kept in README. Sets up daily upstream sync with auto-PR on drift
  in both modes. Trigger on: "deploy to Coolify", "fork and host", "add to
  opensaasapps", "deploy to unboxd", "one-click deploy", "rebrand and deploy", or
  any request to self-host an open-source app on Coolify via Docker Compose.
---

# Coolify One-Click Deploy

Two deployment modes — ask the user which they want before doing anything else:

| Mode | Org | Visibility | Rebranding | License scope |
|---|---|---|---|---|
| **opensaasapps** | `github.com/opensaasapps` | Public | None — upstream as-is | OSI open source only |
| **unboxd.cloud** | `github.com/unboxd-cloud` | **Private** | Full rebrand | OSI open source only |

> ⚠️ **Hard constraints — never override:**
> 1. **Open source only** — OSI-approved license required for both modes. Refuse
>    BSL, SSPL, Elastic, proprietary, or source-available. No exceptions.
> 2. **Upstream credit is mandatory in both modes** — the upstream notice block in
>    README and `UPSTREAM_SYNC.md` must always be present. Never remove or skip.

---

## Step 0 — License Gate (always run first)

1. Fetch `https://api.github.com/repos/{owner}/{repo}/license`
2. Read `license.spdx_id`.

**Allowed:** `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `GPL-2.0`,
`GPL-3.0`, `AGPL-3.0`, `MPL-2.0`, `LGPL-2.1`, `LGPL-3.0`, `ISC`, `Unlicense`

**Blocked — stop immediately:**
`BUSL-1.1`, `SSPL-1.0`, `Elastic-2.0`, `Commons-Clause`, or any
`spdx_id` of `NOASSERTION` / `null` / custom proprietary.

If blocked:
> "⛔ This repo uses **{license_name}**, which is not OSI-approved open source.
> Neither opensaasapps nor unboxd.cloud deployments are possible. No action taken."

Do not offer workarounds. Do not proceed even if the user insists.

---

## Step 0a — Pre-Flight: Rebrand Value Index

> This step is handled by the **rebrand-value-index** skill.
> Skill repo: https://github.com/agentnxxt/agentskills (private)
> Read and invoke it now.
>
> Pass: repo URL, intended use, and candidate mode
> (`unboxd.cloud` or `opensaasapps`).
>
> The skill in turn references:
> - https://github.com/opensaasapps/frameworks/tree/main/rebrand-scoring
> - https://github.com/opensaasapps/frameworks/tree/main/known-brands
>
> The RVI skill returns: `score`, `verdict`, `suggested_mode`, `signals`,
> `breaks[]`, and `survives[]`.

Use the returned values as follows:

| RVI verdict | Action |
|---|---|
| ✅ REBRAND RECOMMENDED | Pre-select unboxd.cloud in Step 0b |
| 🟡 REBRAND POSSIBLE | Present both modes, note the trade-offs from `breaks[]` |
| 🟠 REBRAND NOT RECOMMENDED | Pre-select opensaasapps, warn user, allow override |
| 🔴 REBRAND STRONGLY DISCOURAGED | Pre-select opensaasapps, show full `breaks[]` list, require explicit override to use unboxd.cloud |

Surface the `breaks[]` list as warnings before asking the user to confirm mode.
If `signals.agpl == true` AND mode is unboxd.cloud, always show the AGPL
source-publishing obligation warning regardless of overall score.

If RVI verdict is ✅ and no items in `breaks[]`, skip the confirmation gate
and go straight to Step 0b — no friction for clean deployments.

---

## Step 0b — Mode Selection + Inputs

Ask: **"opensaasapps (public, no rebrand) or unboxd.cloud (private, rebranded)?"**

### opensaasapps mode inputs
| Input | Notes |
|---|---|
| Upstream repo URL | e.g. `https://github.com/n8n-io/n8n` |
| Coolify project name | Default: upstream repo name |
| Branch | Default: auto-detect `main`/`master` |
| Env var overrides | Optional key=value pairs |

### unboxd.cloud mode inputs
| Input | Notes |
|---|---|
| Upstream repo URL | e.g. `https://github.com/n8n-io/n8n` |
| New repo name | e.g. `autoflow` → `github.com/unboxd-cloud/autoflow` (private) |
| New brand name | Display name for README + compose labels |
| Coolify project name | Default: new repo name |
| Branch | Default: auto-detect `main`/`master` |
| Env var overrides | Optional key=value pairs |

---

## Step 0c — Resolve Credentials

Priority order: env var → config file → ask user.

| Credential | Env var | Config key (`~/.config/coolify-deploy/config.json`) |
|---|---|---|
| GitHub Token | `GITHUB_TOKEN` / `GH_TOKEN` | `github_token` (needs `repo` + `write:org`) |
| Coolify API Key | `COOLIFY_API_KEY` | `coolify_api_key` |
| Coolify Base URL | `COOLIFY_BASE_URL` | `coolify_base_url` |

Auto-discover Coolify server + destination:
```
GET {COOLIFY_BASE_URL}/api/v1/servers
GET {COOLIFY_BASE_URL}/api/v1/servers/{server_uuid}/destinations
```
Single server/destination → auto-select. Multiple → show numbered list.

> See `references/coolify-api.md` for full API reference.

---

## Step 1 — Fork the Repo

### opensaasapps mode — public fork, original name
```
POST https://api.github.com/repos/{owner}/{repo}/forks
{ "organization": "opensaasapps", "default_branch_only": false }
```
Poll `GET /repos/opensaasapps/{original_repo_name}` until ready (up to 30s).

### unboxd.cloud mode — private fork, new name
```
POST https://api.github.com/repos/{owner}/{repo}/forks
{ "organization": "unboxd-cloud", "name": "{new_repo_name}", "default_branch_only": false }
```
Then immediately set private:
```
PATCH https://api.github.com/repos/unboxd-cloud/{new_repo_name}
{ "private": true }
```
Poll `GET /repos/unboxd-cloud/{new_repo_name}` until ready (up to 30s).

Clone locally into a temp dir.

---

## Step 2 — Content Changes

### opensaasapps mode — minimal, no rebrand

Only add hosting metadata and sync files. Do not rename anything.

Add to top of `README.md`:
```markdown
> **Hosted by [opensaasapps](https://github.com/opensaasapps)** — curated open-source
> apps, ready to self-host. Upstream: [{upstream_name}]({upstream_url}) · {license_name}
> Sync: tracked automatically — see [UPSTREAM_SYNC.md](UPSTREAM_SYNC.md).
```

Do **not** modify LICENSE. Commit: `chore: add opensaasapps hosting metadata`

---

### unboxd.cloud mode — full rebrand

#### 2a — README (mandatory upstream credit first, then rebrand)

Add as the **very first content** in `README.md`:
```markdown
> **Based on [{upstream_name}]({upstream_url})** — {license_name} licensed, open source.
> Rebranded and privately hosted by [unboxd.cloud](https://unboxd.cloud).
> Upstream changes are tracked automatically — see [UPSTREAM_SYNC.md](UPSTREAM_SYNC.md).
```

Then replace all occurrences of the upstream name (case-insensitive) with
`{new_brand_name}` throughout the rest of the README. Remove upstream badges
referencing the old repo path. The notice block above must never be removed.

#### 2b — LICENSE

- **Permissive (MIT/Apache/BSD/ISC):** Keep original. Prepend:
  `Copyright (c) {year} unboxd.cloud (fork maintainer)` — keep original copyright below.
- **Copyleft (GPL/AGPL/LGPL/MPL):** Keep LICENSE unchanged. Add `NOTICE` file:
  ```
  Fork of {upstream_name} ({upstream_url}).
  Original Copyright (c) {upstream_author}.
  Fork maintained by unboxd.cloud (https://unboxd.cloud).
  ```

#### 2c — Patch docker-compose service names

Find all `docker-compose.yml` / `docker-compose.yaml` / `compose.yml` files.
Rename every service key containing the upstream name → `{new_brand_name}`.
Update all `depends_on`, `links`, `networks`, `container_name` references.

```yaml
# Before                          # After (brand: autoflow)
services:                         services:
  n8n:                              autoflow:
    container_name: n8n               container_name: autoflow
    depends_on: [n8n-postgres]        depends_on: [autoflow-postgres]
  n8n-postgres:                     autoflow-postgres:
```

#### 2d — Commit
```bash
git add -A
git commit -m "chore: rebrand to {new_brand_name} — based on {upstream_url}"
git push origin {branch}
```

---

## Step 3 — Parse Environment Variables

Read all compose files. Extract:
- `environment:` key-value pairs
- `env_file:` references (read those files too)
- No default → **required**; has default → **optional**

Apply user-supplied overrides. Present for review:
```
SERVICE: {service_name}
  REQUIRED:  DB_PASSWORD, ENCRYPTION_KEY
  OPTIONAL:  NODE_ENV=production, PORT=5678, DB_HOST={service_name}-postgres
```
Block until all required vars are supplied.

---

## Step 4 — Deploy to Coolify

> Read `references/coolify-api.md` before making calls.

### 4a — Create/reuse project
```
POST {COOLIFY_BASE_URL}/api/v1/projects
{ "name": "{coolify_project_name}", "description": "coolify-one-click-deploy" }
```

### 4b — Create Docker Compose service

**opensaasapps:** `git_repository: https://github.com/opensaasapps/{original_repo_name}`
**unboxd.cloud:** `git_repository: https://github.com/unboxd-cloud/{new_repo_name}`

```
POST {COOLIFY_BASE_URL}/api/v1/services
{
  "type": "docker-compose",
  "name": "{repo_name}",
  "git_repository": "{git_repository}",
  "git_branch": "{branch}",
  "project_uuid": "{project_uuid}",
  "server_uuid": "{server_uuid}",
  "destination_uuid": "{destination_uuid}",
  "docker_compose_location": "/docker-compose.yml"
}
```
Capture `service_uuid`.

### 4c — Bulk wire env vars
```
POST {COOLIFY_BASE_URL}/api/v1/services/{service_uuid}/envs/bulk
{ "data": [{ "key": "X", "value": "y", "is_secret": false }, ...] }
```
Mark as secret if name contains: `PASSWORD`, `SECRET`, `KEY`, `TOKEN`,
`PRIVATE`, `CREDENTIAL`, `API_KEY`.

### 4d — Deploy + poll
```
POST {COOLIFY_BASE_URL}/api/v1/deploy?uuid={service_uuid}&force=false
```
Poll `GET /api/v1/services/{service_uuid}` every 5s until `status: running`.

---

## Step 5 — Upstream Sync

Write `.github/workflows/upstream-sync.yml` from `assets/upstream-sync-action.yml`.
Fill in: `UPSTREAM_URL`, `SYNC_BRANCH`, `REPO_NAME`.

Create `UPSTREAM_SYNC.md`:
```markdown
# Upstream Sync

Tracks [{upstream_name}]({upstream_url}).
A GitHub Action runs daily — opens a PR when upstream has new commits.
Review diff for rebranding conflicts before merging.

## Manual sync
git remote add upstream {upstream_url}
git fetch upstream && git merge upstream/{branch}
```

Commit and push both files.

---

## Step 6 — Sponsorship (mandatory for unboxd.cloud, strongly encouraged for opensaasapps)

> **Policy:** If you are white-labelling or commercially benefiting from an
> open-source project, you must become a sponsor. This is non-negotiable for
> unboxd.cloud mode. For opensaasapps mode it is strongly encouraged and the
> skill will prompt the user to do it.

### 6a — Find sponsorship options

Check the upstream repo for funding links in this order:

1. `GET https://api.github.com/repos/{owner}/{repo}` → check `funding_url` field
2. Check repo root for: `FUNDING.yml`, `.github/FUNDING.yml`
3. Check README for: "sponsor", "opencollective", "patreon", "github sponsors",
   "ko-fi", "liberapay", "buymeacoffee", "donate"
4. Check the org's GitHub Sponsors page:
   `https://github.com/sponsors/{owner}`

Parse `.github/FUNDING.yml` — it lists all funding platforms:
```yaml
# Example FUNDING.yml
github: [maintainer-username]
open_collective: project-name
patreon: project-page
custom: https://project.com/donate
```

### 6b — Present sponsorship options to user

Always show this block — never skip it, even if the user seems in a hurry:

```
💝 SPONSORSHIP — {upstream_name}

   You are {deploying a white-label / hosting a public fork} of {upstream_name},
   maintained by {upstream_org}. Please consider supporting the project.

   Available sponsorship options:
   {list each found option with its URL, e.g.}
   ⭐ GitHub Sponsors:   https://github.com/sponsors/{maintainer}
   💛 Open Collective:   https://opencollective.com/{project}
   ☕ Ko-fi:             https://ko-fi.com/{project}

   Suggested monthly amount:
   {tier guidance — see below}

   {If unboxd.cloud mode:}
   ⚠️  Sponsorship is required policy for unboxd.cloud deployments.
       Please confirm you have sponsored or will sponsor this project.

   {If opensaasapps mode:}
   🙏 Sponsorship is strongly encouraged. The project is free to use
       but the maintainers depend on community support.
```

### 6c — Sponsorship amount

Do not suggest a specific amount. Show the upstream's actual tiers from their
sponsorship page (fetched in 6a) and let the user decide freely. If no tiers
are listed, show the link and say:
> "Choose whatever amount reflects the value this project brings you."

### 6d — Log sponsorship intent

Ask:
> "Have you sponsored or do you plan to sponsor {upstream_name}?
> (yes / will do / skip)"

- **yes / will do** → record confirmed, proceed to Step 6e.
- **skip** (unboxd.cloud) → firm reminder with link, proceed to Step 6e.
- **skip** (opensaasapps) → acknowledge, proceed to Step 6e.

### 6e — Issue UnboxdBadge

> This step calls the **unboxd-badges** skill.
> Skill repo: https://github.com/agentnxxt/agentskills (private)
> Read and invoke it now.

Call unboxd-badges with:
```json
{
  "action": "issue",
  "recipient": {
    "github_username": "{deployer_github_username}"
  },
  "skill": "IT infrastructure",
  "sfia_level": null,
  "evidence": {
    "type": "deployment",
    "url": "https://github.com/{org}/{repo_name}",
    "description": "Forked, {rebranded,} and deployed {upstream_name} to Coolify with Docker Compose, env var wiring, upstream sync{, and OSS sponsorship}."
  },
  "context": "{opensaasapps | unboxd.cloud} one-click deploy of {upstream_name}"
}
```

Add the returned `readme_badge` to the fork's README under the upstream
credit block:
```markdown
[![UnboxdBadge](https://badges.unboxd.cloud/{id}/shield.svg)](https://badges.unboxd.cloud/{id})
```

---

## Step 7 — Summary

### opensaasapps
```
✅ OPENSAASAPPS DEPLOY COMPLETE
📦 Fork (public):  https://github.com/opensaasapps/{original_repo_name}
🔁 Upstream:       {upstream_url} · {license_name}
🚀 Coolify URL:    {public_url}
🔑 Env vars:       {n} wired ({m} secrets)
🔄 Sync:           Daily → PR on drift
💝 Sponsorship:    {confirmed | reminder sent} → {best_sponsorship_url}
🏅 UnboxdBadge:    {badge_url} · SFIA ITOP · pending verification
```

### unboxd.cloud
```
✅ UNBOXD.CLOUD DEPLOY COMPLETE
📦 Fork (private): https://github.com/unboxd-cloud/{new_repo_name}
🏷️  Brand:          {new_brand_name}
🔁 Upstream:       {upstream_url} · {license_name}
🚀 Coolify URL:    {public_url}
🔑 Env vars:       {n} wired ({m} secrets)
🔄 Sync:           Daily → PR on drift
⚖️  Credit:         Upstream attribution preserved in README
💝 Sponsorship:    {confirmed | reminder sent} → {best_sponsorship_url}
🏅 UnboxdBadge:    {badge_url} · SFIA ITOP · pending verification
```

---

## Error Handling

| Situation | Action |
|---|---|
| Non-OSI license | Refuse at Step 0 — no exceptions |
| Fork already exists | Ask: reuse or delete + re-fork? |
| Token lacks org access | Explain: needs `repo` + `write:org` scopes |
| Private fork fails | Check org plan — may need paid GitHub plan |
| Compose file not found | Ask user to specify path |
| Required env var missing | Block, re-prompt |
| Coolify API 4xx | Show full error + suggestion |
| Deployment fails | Fetch and display Coolify deployment logs |

---

## Reference Files

- `references/coolify-api.md` — Coolify API v1 endpoint reference
- `assets/upstream-sync-action.yml` — GitHub Action template for upstream sync
