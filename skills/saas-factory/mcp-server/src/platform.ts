export const PLATFORM_CAPABILITIES = `
# Platform Capabilities

## Data Ingestion Module

### Tenant-Scoped Data Import
- [ ] Bulk import endpoint: POST /api/v1/import
  - Accepts: CSV, JSON, JSONL, XML
  - Max file size configurable per plan tier
  - Async processing for large files (return job ID, poll for status)
- [ ] Import job tracking: GET /api/v1/import/jobs/:id
  - Status: pending, processing, completed, failed, partially_failed
  - Progress: rows_processed, rows_succeeded, rows_failed, error_details
- [ ] All imported data auto-tagged with tenant_id (never trust client-provided tenant_id)
- [ ] Data validation on import: schema validation, type checking, duplicate detection
- [ ] Idempotent imports: upsert mode with configurable dedup key

### Data Pipeline Integration
- [ ] Webhook receiver: POST /api/v1/ingest/webhook
  - HMAC signature verification on incoming webhooks
  - Tenant routing: map external source to tenant via API key or webhook secret
- [ ] Event ingestion: POST /api/v1/ingest/events (streaming data)
  - Batch support: array of events in single request
  - Rate limited per tenant plan
- [ ] ETL/ELT hooks: pre-transform and post-transform hooks for custom data mapping
- [ ] Dead letter queue: failed events stored for retry/inspection

### Data Export
- [ ] Bulk export: POST /api/v1/export (CSV, JSON, JSONL)
  - Async for large datasets (job-based)
  - Tenant-scoped: only current tenant's data
- [ ] Scheduled exports: recurring exports via cron/background job
- [ ] Export to external systems: webhook delivery of export files

## Audit Log System

### Event Capture
- [ ] Audit log schema:
  - id, tenant_id, actor_id, actor_type (user/service_account/system/agent)
  - action (create, read, update, delete, login, logout, export, import, role_change)
  - resource_type, resource_id
  - changes (JSON diff: { field: { old: X, new: Y } })
  - ip_address, user_agent, request_id, timestamp
- [ ] Append-only: audit records are immutable (no UPDATE/DELETE)
- [ ] Write-ahead: audit record written before or in same transaction as action

### Events to Capture
- [ ] Authentication: login, logout, login_failed, password_changed, mfa_enabled/disabled
- [ ] Authorization: role_changed, access_requested/approved/denied/revoked
- [ ] Data: record CRUD, bulk_import, bulk_export
- [ ] Admin: tenant CRUD, plan_changed, settings_changed
- [ ] Billing: subscription events, payment events
- [ ] Identity: user provisioned/deprovisioned, API key CRUD
- [ ] System: migration_run, deployment_started, config_changed

### Audit Log API
- [ ] GET /api/v1/audit-logs — tenant-scoped query
  - Filters: actor_id, action, resource_type, resource_id, date_range
  - Cursor-based pagination
- [ ] GET /api/v1/admin/audit-logs — platform-wide (admin only)
- [ ] POST /api/v1/audit-logs/export — export as CSV/JSON
- [ ] Retention: configurable per plan (free: 30d, starter: 90d, pro: 1yr, enterprise: unlimited)

### Audit Log Integrity
- [ ] Hash chaining: each record includes hash of previous (tamper detection)
- [ ] Periodic integrity verification via background job
- [ ] External log shipping: forward to SIEM (Splunk, ELK, Datadog) via webhook/syslog

## Changelog Publishing

### Platform Changelog (Internal Releases)
- [ ] Changelog model: id, version (semver), title, body (markdown), category (feature/fix/breaking/security/deprecation), published_at, author
- [ ] Admin: POST /api/v1/admin/changelog — create entry
- [ ] Public: GET /api/v1/changelog — list entries (paginated)
- [ ] GET /api/v1/changelog/latest — most recent
- [ ] RSS/Atom feed: GET /api/v1/changelog/feed.xml

### Tenant-Facing Notifications
- [ ] In-app notification: unread changelog entries shown on login
- [ ] Email digest: weekly or per-release summary to tenant admins
- [ ] Webhook delivery: changelog events to tenant webhook URLs
- [ ] "What's new" badge in UI (dismiss on read)
- [ ] User preference: opt-in/out of changelog notifications

### API Changelog (Developer-Facing)
- [ ] Breaking changes documented per API version
- [ ] Deprecation notices with sunset dates
- [ ] Migration guides for breaking changes
- [ ] Versioned OpenAPI specs published alongside changelog

### Tenant Activity Feed
- [ ] GET /api/v1/activity — human-readable activity feed
  - "Alice updated project settings"
  - "Bob was added as member by Carol"
  - "API key 'ci-pipeline' was rotated"
- [ ] Filterable by: actor, action type, date range
- [ ] Real-time: WebSocket or SSE endpoint for live feed
`;

export function getPlatformCapabilities(): string {
  return PLATFORM_CAPABILITIES;
}
