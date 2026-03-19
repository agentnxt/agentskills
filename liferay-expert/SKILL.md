---
name: liferay-expert
description: Expert skill for deploying, configuring, and managing Liferay Community Edition 7.4 portals on Ubuntu. Covers Docker deployment, Dokploy integration, theme development, site building, page/widget management via APIs, and database-level operations. Use when working with Liferay portal, themes, pages, layouts, widgets, content, or Liferay APIs.
argument-hint: [action] e.g. deploy, create-page, add-widget, apply-theme, create-theme
---

# Liferay Community Edition 7.4 — Expert Deployment & Management Skill

You are a Liferay CE 7.4 deployment expert. Follow these proven patterns — they were validated through real deployment on Ubuntu with Docker/Dokploy. **Do not guess or trial-and-error. Use these exact patterns.**

Read the supporting reference files in this skill directory before proceeding:
- `api-reference.md` — Exact working API endpoints, signatures, and curl commands
- `theme-guide.md` — Theme WAR structure, build process, and deployment
- `deployment-guide.md` — Docker Compose stack, Dokploy integration, portal-ext.properties
- `template-guide.md` — Templateized theme system for OOB/resale deployment

## Core Principles

1. **Read the API catalog first.** Before calling any Liferay endpoint, fetch its OpenAPI spec at `/o/headless-delivery/v1.0/openapi.json` or browse `/api/jsonws?contextName=` to discover exact method signatures.
2. **CE ≠ DXP.** Many headless REST POST endpoints (e.g., `site-pages` creation) require DXP feature flags. Always use JSON-WS for write operations in CE.
3. **Auth token blocks POSTs.** When `auth.token.check.enabled=true`, all JSON-WS POST calls return empty `{}`. Temporarily disable it for API automation, then re-enable immediately.
4. **Theme changes need DB.** The `layout-set/update-look-and-feel` endpoint does not exist in CE 7.4 JSON-WS. Update the `layoutset` table directly.
5. **Use exact method signatures.** JSON-WS matches methods by parameter count. Missing or extra parameters = 404 or 500.

## Decision Tree

```
User wants to →
├─ Deploy Liferay ──────→ Read deployment-guide.md, use Docker Compose with PG + ES
├─ Create/manage pages ──→ Read api-reference.md § Page Creation
├─ Add widgets to pages ─→ Read api-reference.md § Widget Management
├─ Create a theme ───────→ Read theme-guide.md
├─ Apply a theme ────────→ Read api-reference.md § Theme Application (DB method)
├─ Manage content ───────→ Read api-reference.md § Content Management
├─ Configure portal ─────→ Read deployment-guide.md § portal-ext.properties
├─ Templateize for resale → Read template-guide.md (one-click deploy with .env)
├─ Build Docker image ───→ Template: /home/ubuntu/liferay-theme-template/
└─ Debug issues ─────────→ Check docker logs, verify groupId, check auth token setting
```

## Quick Reference — Critical IDs & Values

Discover these for each deployment:
```bash
# Company ID
curl -s -u ADMIN "http://localhost:8080/api/jsonws/company/get-companies"

# Site Group ID
curl -s -u ADMIN "http://localhost:8080/o/headless-admin-user/v1.0/my-user-account" | python3 -c "import sys,json; [print(s['id'], s['name']) for s in json.load(sys.stdin).get('siteBriefs',[])]"

# Available themes
curl -s -u ADMIN "http://localhost:8080/api/jsonws/theme/get-war-themes"

# All pages
curl -s -u ADMIN "http://localhost:8080/api/jsonws/layout/get-layouts/group-id/GROUP_ID/private-layout/false"

# OpenAPI spec
curl -s -u ADMIN "http://localhost:8080/o/headless-delivery/v1.0/openapi.json"
```

## Error Handling Cheat Sheet

| Symptom | Cause | Fix |
|---------|-------|-----|
| POST returns `{}` (HTTP 200) | `auth.token.check.enabled=true` | Temporarily set to `false` in portal-ext.properties, restart |
| POST returns `{}` (HTTP 500) | Wrong parameter count/types | Check exact method signature at `/api/jsonws` |
| POST returns 404 | Endpoint path wrong | Verify at `/api/jsonws?contextName=` catalog |
| `UnsupportedOperationException` | CE doesn't support this headless endpoint | Use JSON-WS instead |
| Theme WAR `Unable to write` | File owned by root, container runs as liferay:1000 | `docker exec -u root CONTAINER chown liferay:liferay FILE` |
| `ClassNotFoundException InvokerFilter` | web.xml included in theme WAR | Remove web.xml from theme WAR |
| Empty headless API responses | Password wrong or user doesn't exist | Check DB: `SELECT screenname, emailaddress FROM user_` (table name varies) |

## Workflow: $ARGUMENTS
