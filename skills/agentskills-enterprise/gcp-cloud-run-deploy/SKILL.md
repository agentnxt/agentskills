---
name: gcp-cloud-run-deploy
description: >
  Full-lifecycle deployment of GitHub repos to Google Cloud Run using the Cloud Run Admin API v2,
  with Cloud Build for image building, CI/CD pipeline setup (GitHub Actions + Cloud Build triggers),
  Metabase dashboard configuration for monitoring, and alerting via webhooks or email.
  Use this skill whenever the user wants to deploy to Cloud Run, set up GCP CI/CD pipelines,
  configure monitoring dashboards with Metabase for GCP services, or create alerts for Cloud Run
  services. Also trigger when the user mentions "deploy to GCP", "Cloud Run deployment",
  "GCP CI/CD", "Cloud Run monitoring", "Metabase dashboards for GCP", or any combination of
  deploying containers to Google Cloud with observability. Even if they just say "deploy this to
  Google Cloud" or "set up monitoring for my Cloud Run service" — this skill applies.
---

# GCP Cloud Run Deploy

A comprehensive skill for deploying GitHub repositories to Google Cloud Run with full CI/CD,
monitoring, and alerting — all via direct REST API calls (never CLI).

## Core Principle: API-First, Never CLI

**NEVER use `gcloud` CLI if a REST API exists.** Always use direct HTTP API calls because:

- **Audit trails** — every API call is logged in Cloud Audit Logs with caller identity, timestamp, and request details
- **Standard authentication** — OAuth2 bearer tokens from service accounts follow GCP's IAM best practices
- **No CLI dependency** — the skill works anywhere Python runs, no `gcloud` SDK installation required
- **Reproducibility** — raw API calls are explicit and deterministic with no hidden CLI defaults
- **Traceability** — service account tokens are revocable and tied to specific IAM roles

The only exception: if a specific operation has NO REST API equivalent (rare), document why CLI is necessary and get user confirmation before using it.

**This includes CI/CD templates.** When generating GitHub Actions workflows or Cloud Build configs, use the OAuth2 token from the service account (via JWT exchange or Workload Identity Federation) in `curl` calls — do NOT use `gcloud auth print-access-token` even inside GCP's own build environment. The token is already available from the auth step; piping it through `gcloud` adds an unnecessary CLI dependency and breaks the audit trail principle.

## Authentication

Use **service account key JSON** with least-privilege IAM roles.

### Token Exchange Flow

```
Service Account Key JSON
  → POST https://oauth2.googleapis.com/token
    (grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer, assertion=signed_jwt)
  → Access Token (Bearer)
  → Use in Authorization header for all API calls
```

### Required IAM Roles (Least Privilege)

Ask the user for their GCP project ID and service account email. Then recommend ONLY the roles needed:

| Role | Purpose | When Needed |
|------|---------|-------------|
| `roles/run.admin` | Create/update/delete Cloud Run services | Always |
| `roles/cloudbuild.builds.editor` | Trigger and manage Cloud Build builds | When building images |
| `roles/artifactregistry.writer` | Push container images to Artifact Registry | When building images |
| `roles/iam.serviceAccountUser` | Act as the Cloud Run service account | Always |
| `roles/monitoring.editor` | Create/manage monitoring alert policies | When setting up alerts |
| `roles/logging.viewer` | Read Cloud Logging for monitoring | When analyzing metrics |

Before proceeding with deployment, confirm with the user that these roles are assigned. Provide the exact API call to check:

```
GET https://cloudresourcemanager.googleapis.com/v1/projects/{PROJECT_ID}:getIamPolicy
Authorization: Bearer {TOKEN}
```

## Workflow Overview

The skill follows this sequence. At each major step, **confirm with the user before proceeding**.

```
1. ANALYZE  → Scan repo: detect Dockerfile, language, framework, ports
2. CONFIRM  → Present findings and proposed config to user
3. BUILD    → Trigger Cloud Build to build image → Artifact Registry
4. DEPLOY   → Create/update Cloud Run service via Admin API v2
5. CI/CD    → Set up GitHub Actions and/or Cloud Build trigger
6. MONITOR  → Configure Metabase dashboards with auto-suggested metrics
7. ALERT    → Set up alerting via GCP Monitoring, webhooks, or email
```

---

## Step 1: Analyze Repository

Scan the GitHub repository to auto-detect:

- **Dockerfile presence** — check root and common subdirectories
- **Language/framework** — from package.json, requirements.txt, go.mod, pom.xml, etc.
- **Exposed port** — from Dockerfile EXPOSE, or framework defaults (3000 for Node, 8080 for Go, 8000 for Python)
- **Environment variables** — from .env.example, docker-compose.yml, or framework config
- **Entry point** — from Dockerfile CMD/ENTRYPOINT or Procfile

If no Dockerfile is found, inform the user and offer to generate one based on the detected stack. **Always confirm before creating any files.**

Present findings to the user:

```
Detected:
- Language: Python 3.11 (FastAPI)
- Dockerfile: Found at ./Dockerfile
- Port: 8000
- Env vars: DATABASE_URL, API_KEY, SECRET_KEY

Shall I proceed with these settings, or do you want to adjust anything?
```

---

## Step 2: Build Image via Cloud Build API

Use the **Cloud Build API v1** to build and push the Docker image.

### API: Create Build

```
POST https://cloudbuild.googleapis.com/v1/projects/{PROJECT_ID}/builds
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "source": {
    "repoSource": {
      "projectId": "{PROJECT_ID}",
      "repoName": "{REPO_NAME}",
      "branchName": "{BRANCH}"
    }
  },
  "steps": [
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:{TAG}", "."]
    }
  ],
  "images": [
    "{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:{TAG}"
  ]
}
```

### API: Check Build Status

```
GET https://cloudbuild.googleapis.com/v1/projects/{PROJECT_ID}/builds/{BUILD_ID}
Authorization: Bearer {TOKEN}
```

Poll until `status` is `SUCCESS` or `FAILURE`. Report progress to user.

### Artifact Registry Setup

If the Artifact Registry repository doesn't exist, create it first:

```
POST https://artifactregistry.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/repositories
Authorization: Bearer {TOKEN}

{
  "format": "DOCKER",
  "repositoryId": "{REPO_NAME}"
}
```

---

## Step 3: Deploy to Cloud Run via Admin API v2

### Create vs Update: Check First, Then Act

Before deploying, ALWAYS check if the service exists first with a GET call. This determines whether to POST (create) or PATCH (update):

```
GET https://run.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_ID}
Authorization: Bearer {TOKEN}
```

- **404** → service doesn't exist → use POST to create
- **200** → service exists → use PATCH to update with new revision

This distinction matters because POST on an existing service will fail with 409 Conflict, and PATCH on a non-existent service will fail with 404. Always check first.

### API: Create Service

```
POST https://run.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/services?serviceId={SERVICE_ID}
Authorization: Bearer {TOKEN}

{
  "template": {
    "containers": [
      {
        "image": "{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO}/{IMAGE}:{TAG}",
        "ports": [{"containerPort": {PORT}}],
        "env": [
          {"name": "KEY", "value": "value"},
          {"name": "SECRET_KEY", "valueSource": {"secretKeyRef": {"secret": "projects/{PROJECT_ID}/secrets/{SECRET_NAME}", "version": "latest"}}}
        ],
        "resources": {
          "limits": {"cpu": "1", "memory": "512Mi"}
        }
      }
    ],
    "scaling": {
      "minInstanceCount": 0,
      "maxInstanceCount": 10
    }
  },
  "ingress": "INGRESS_TRAFFIC_ALL",
  "launchStage": "GA"
}
```

### API: Update Service (New Revision)

```
PATCH https://run.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_ID}
Authorization: Bearer {TOKEN}

{
  "template": {
    "containers": [
      {
        "image": "{NEW_IMAGE_URI}"
      }
    ]
  }
}
```

### API: Get Service Status

```
GET https://run.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_ID}
Authorization: Bearer {TOKEN}
```

Verify the service is `READY` before reporting success. Provide the service URL to the user.

### Handling Secrets

For environment variables containing secrets, **never hardcode values**. Use GCP Secret Manager:

```
POST https://secretmanager.googleapis.com/v1/projects/{PROJECT_ID}/secrets
Authorization: Bearer {TOKEN}

{"replication": {"automatic": {}}}
```

Then reference secrets in the Cloud Run service config via `secretKeyRef`.

---

## Step 4: CI/CD Pipeline Setup

Support **both** GitHub Actions and Cloud Build triggers. Ask the user which they prefer, or set up both.

### Option A: GitHub Actions

Generate a `.github/workflows/deploy.yml` file. Read `references/ci-cd-github-actions.md` for the full template.

Key points:
- Use Workload Identity Federation (preferred) or service account key for auth
- Build image via Cloud Build API (not docker CLI)
- Deploy via Cloud Run Admin API (not `gcloud`)
- Include staging → production promotion pattern
- Always confirm the workflow file with the user before creating

### Option B: Cloud Build Trigger

Create a Cloud Build trigger via API:

```
POST https://cloudbuild.googleapis.com/v1/projects/{PROJECT_ID}/triggers
Authorization: Bearer {TOKEN}

{
  "name": "{TRIGGER_NAME}",
  "github": {
    "owner": "{GITHUB_OWNER}",
    "name": "{GITHUB_REPO}",
    "push": {
      "branch": "^main$"
    }
  },
  "build": {
    "steps": [...],
    "images": [...]
  }
}
```

### Present Cost Implications

Before setting up CI/CD, inform the user:

```
Cost considerations:
- Cloud Build: First 120 build-minutes/day free, then $0.003/build-minute
- GitHub Actions: 2,000 minutes/month free (public repos unlimited)
- Artifact Registry: $0.10/GB/month storage

Which would you prefer, or should I set up both?
```

---

## Step 5: Monitoring with Metabase

The user provides their Metabase instance URL and credentials. Read `references/metabase-setup.md` for detailed API reference.

### Connect to Metabase

```
POST {METABASE_URL}/api/session
Content-Type: application/json

{"username": "{EMAIL}", "password": "{PASSWORD}"}
```

### Auto-Suggest Metrics

Analyze the deployed service and infrastructure to suggest relevant metrics. Base suggestions on:

- **Code analysis** — if the app has database queries, suggest query latency; if it has external API calls, suggest upstream latency
- **Infrastructure** — Cloud Run always has: request count, latency (p50/p95/p99), error rate, instance count, memory/CPU usage, cold start count
- **Cost** — billable container instance time

Present suggestions to the user:

```
Based on your FastAPI app with PostgreSQL:

Recommended dashboards:
1. Service Health — request rate, error rate (4xx/5xx), latency p50/p95/p99
2. Resource Usage — CPU utilization, memory usage, instance count
3. Database — query latency, connection pool usage
4. Cost — billable instance time, request volume trends

Which of these would you like me to set up? Or suggest different ones?
```

### Data Source

Metabase dashboards query data from one of:
- **BigQuery** — if the user exports Cloud Monitoring metrics to BigQuery
- **Cloud SQL / PostgreSQL** — if the user has a metrics database
- **Google Sheets** — lightweight option for small setups

Ask the user which data source to configure.

### Create Dashboard via API

```
POST {METABASE_URL}/api/dashboard
Content-Type: application/json
X-Metabase-Session: {SESSION_TOKEN}

{
  "name": "Cloud Run - {SERVICE_NAME}",
  "description": "Monitoring dashboard for {SERVICE_NAME}",
  "collection_id": {COLLECTION_ID}
}
```

Then create questions (cards) and add them to the dashboard. See `references/metabase-setup.md` for the full card creation flow.

---

## Step 6: Alerting

Auto-recommend the best alerting approach based on the user's setup, with cost implications.

### Decision Matrix

| Approach | Best For | Cost | Setup Complexity |
|----------|----------|------|------------------|
| GCP Cloud Monitoring | Standard metrics (latency, errors, uptime) | Free for Cloud Run metrics, $0.2580/notification after free tier | Low |
| Custom webhook script | Custom business metrics, multi-service correlation | Compute cost for the script runner | Medium |
| Email (SMTP) | Simple notifications, no external service dependency | Free (if using GCP SMTP relay or existing SMTP server) | Low |
| Email (SendGrid) | High volume, deliverability tracking | Free tier: 100 emails/day | Low-Medium |

Present this to the user and let them choose.

### GCP Cloud Monitoring Alert Policy (via API)

```
POST https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/alertPolicies
Authorization: Bearer {TOKEN}

{
  "displayName": "{SERVICE_NAME} - High Error Rate",
  "conditions": [
    {
      "displayName": "Error rate > 5%",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"{SERVICE_NAME}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 5,
        "duration": "60s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE"
          }
        ]
      }
    }
  ],
  "notificationChannels": ["{CHANNEL_ID}"],
  "combiner": "OR"
}
```

### Webhook Notification Channel

```
POST https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/notificationChannels
Authorization: Bearer {TOKEN}

{
  "type": "webhook_token_auth",
  "displayName": "{SERVICE_NAME} Webhook",
  "labels": {
    "url": "{WEBHOOK_URL}"
  }
}
```

### Email Notification Channel

```
POST https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/notificationChannels
Authorization: Bearer {TOKEN}

{
  "type": "email",
  "displayName": "{SERVICE_NAME} Email Alert",
  "labels": {
    "email_address": "{EMAIL}"
  }
}
```

### Suggested Alert Policies

Based on Cloud Run best practices, always suggest these baseline alerts:

1. **High error rate** — 5xx responses > 5% over 5 minutes
2. **High latency** — p99 latency > 2 seconds over 5 minutes
3. **Instance scaling** — instance count at max for > 10 minutes (may need scaling adjustment)
4. **Cold start spike** — cold start rate > 20% (indicates scaling or min-instance tuning needed)

Confirm thresholds with the user — they know their SLAs better than defaults.

---

## Scripts

The `scripts/` directory contains helper scripts. These handle the OAuth2 token exchange, API calls, and common operations. Use them instead of writing API calls from scratch each time:

- `scripts/auth.py` — Service account key → OAuth2 bearer token exchange
- `scripts/deploy.py` — Build image + deploy to Cloud Run
- `scripts/monitoring.py` — Set up Metabase dashboards
- `scripts/alerts.py` — Create GCP Monitoring alert policies and notification channels

Run scripts with: `python scripts/<script>.py --help` for usage.

---

## Error Handling

For every API call:
1. Check HTTP status code
2. On 401/403 — token expired or insufficient permissions → re-authenticate or report missing IAM role
3. On 404 — resource doesn't exist → offer to create it
4. On 409 — conflict (resource already exists) → offer to update instead
5. On 429 — rate limited → back off and retry with exponential backoff

Always show the user the full error response body for debugging.

---

## Execution Cost Summary

At the end of every skill execution, present a **cost summary** to the user with two separate sections:

### Google Cloud API Costs

Track and display every GCP API call made during the session:

```
┌─────────────────────────────────────────────────────────────┐
│  Google Cloud API Cost Summary                              │
├─────────────────────────┬───────────┬───────────────────────┤
│ Service                 │ API Calls │ Estimated Cost        │
├─────────────────────────┼───────────┼───────────────────────┤
│ Cloud Build             │ 2         │ ~$0.003/build-min     │
│ Cloud Run Admin API     │ 4         │ Free (admin ops)      │
│ Artifact Registry       │ 1         │ ~$0.10/GB/month       │
│ Secret Manager          │ 3         │ $0.06/10K accesses    │
│ Cloud Monitoring        │ 5         │ Free (first 150MB)    │
│ IAM / Resource Manager  │ 2         │ Free                  │
├─────────────────────────┼───────────┼───────────────────────┤
│ TOTAL ESTIMATED         │ 17        │ ~$X.XX                │
└─────────────────────────┴───────────┴───────────────────────┘

Ongoing monthly costs:
- Cloud Run: $0.00002400/vCPU-sec, $0.00000250/GiB-sec, 2M requests/month free
- Artifact Registry storage: $0.10/GB/month
- Cloud Monitoring alerts: Free for first 100 policies
```

### Anthropic API Costs (Claude Usage)

Track the tokens consumed by this skill execution:

```
┌─────────────────────────────────────────────────────────────┐
│  Anthropic API Cost Summary (This Session)                  │
├─────────────────────────┬───────────────────────────────────┤
│ Input tokens            │ ~XX,XXX                           │
│ Output tokens           │ ~XX,XXX                           │
│ Estimated cost          │ ~$X.XX                            │
├─────────────────────────┴───────────────────────────────────┤
│ Pricing: Opus $15/M input, $75/M output                    │
│          Sonnet $3/M input, $15/M output                    │
│          Haiku $0.25/M input, $1.25/M output                │
└─────────────────────────────────────────────────────────────┘
```

The purpose of this summary is transparency — the user should know exactly what they're paying for, both on the GCP side and the AI side. This builds trust and helps the user make informed decisions about future runs.

---

## Safety Checklist

Before ANY deployment or infrastructure change, verify:

- [ ] User has confirmed the GCP project ID
- [ ] Service account has only the required IAM roles (least privilege)
- [ ] No secrets are hardcoded — all sensitive values use Secret Manager
- [ ] The user has reviewed and approved the Cloud Run service configuration
- [ ] For production deployments: traffic splitting is configured (canary/blue-green) unless user opts out
- [ ] Alert notification channels are verified (test webhook/email before going live)
