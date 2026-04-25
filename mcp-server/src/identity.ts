export const IDENTITY_GOVERNANCE = `
# Identity & Access Governance

## IAM / IdP Integration (Identity Provider Compatibility)

### SAML 2.0 Support
- [ ] SP-initiated SSO flow implemented
- [ ] IdP-initiated SSO flow supported
- [ ] SAML metadata endpoint exposed (GET /saml/metadata)
- [ ] ACS (Assertion Consumer Service) endpoint implemented
- [ ] SLO (Single Logout) supported
- [ ] Certificate rotation mechanism in place
- [ ] Compatible with: Okta, Azure AD, OneLogin, PingIdentity, Google Workspace, JumpCloud

### OIDC / OAuth 2.0 Support
- [ ] Authorization Code flow with PKCE implemented
- [ ] Discovery endpoint (/.well-known/openid-configuration) exposed if acting as provider
- [ ] Support for external OIDC providers (Okta, Azure AD, Keycloak, Auth0)
- [ ] Token exchange and claims mapping for tenant context
- [ ] Scope-based access control aligned with RBAC roles
- [ ] ID token validation (signature, issuer, audience, expiry)

### SCIM 2.0 Support (User Provisioning)
- [ ] SCIM /Users endpoint (GET, POST, PUT, PATCH, DELETE)
- [ ] SCIM /Groups endpoint (GET, POST, PUT, PATCH, DELETE)
- [ ] Filter support (userName eq "...", emails eq "...")
- [ ] Bulk operations support
- [ ] Auto-provision users on first SCIM push
- [ ] Auto-deprovision (deactivate) on SCIM delete
- [ ] Map SCIM groups to tenant roles (admin, member, viewer)
- [ ] Compatible with: Okta SCIM, Azure AD provisioning, OneLogin provisioning

### How to Verify IdP Integration
1. Configure a test IdP (Okta dev account or Keycloak local instance)
2. Initiate SSO login → verify user created/updated in app with correct tenant
3. Push SCIM user create → verify user appears in tenant
4. Push SCIM user delete → verify user deactivated

## IGA (Identity Governance & Administration)

### Access Certification
- [ ] API endpoint to list all users and their roles per tenant (for access reviews)
- [ ] GET /api/v1/admin/access-report → returns user-role-tenant mappings
- [ ] Support for bulk role revocation
- [ ] Audit trail for all role changes (who changed what, when)
- [ ] Timestamp tracking for last login per user (for dormant account detection)

### Lifecycle Management
- [ ] Joiner: Auto-assign default role on provisioning (via SCIM or SSO JIT)
- [ ] Mover: Support role change via API or SCIM group update
- [ ] Leaver: Deactivate on SCIM deprovision, revoke all sessions + API keys
- [ ] Orphan account detection: flag users with no recent login (>90 days)

### Separation of Duties (SoD)
- [ ] Role hierarchy defined (viewer < member < admin < owner)
- [ ] No user can self-elevate roles
- [ ] Owner role changes require another owner's approval (or admin API)
- [ ] API key creation requires admin or owner role

## PAM (Privileged Access Management)

### Admin Access Controls
- [ ] Admin/superadmin actions require MFA or re-authentication
- [ ] Admin API endpoints behind separate auth (ADMIN_SECRET or elevated JWT)
- [ ] All admin actions logged with actor, action, target, timestamp
- [ ] Admin session timeout shorter than regular sessions (<=30 min)
- [ ] Break-glass procedure documented for emergency access

### API Key Management
- [ ] API keys scoped to specific permissions (read, write, admin)
- [ ] API key expiration enforced (max 1 year, configurable)
- [ ] API key last-used tracking (flag unused keys >90 days)
- [ ] API key rotation mechanism (create new, deprecate old)
- [ ] Immediate revocation capability (takes effect within seconds)

### Service Account Controls
- [ ] Service accounts have dedicated tenant membership type
- [ ] Service accounts cannot access admin UI
- [ ] Service account actions attributed in audit log
- [ ] Service account credentials rotated on schedule

## Agentic User Lifecycle Management

### Automated Provisioning & Deprovisioning
- [ ] Event-driven user lifecycle (webhook/SCIM triggers, not manual)
- [ ] Joiner workflow: IdP user create → auto-provision with default role + tenant
- [ ] Mover workflow: IdP group change → auto-update role (no manual intervention)
- [ ] Leaver workflow: IdP user deactivate → cascade: revoke sessions, keys, deactivate, notify admin
- [ ] Rehire workflow: Reactivate previously deprovisioned user with prior role (configurable)
- [ ] Dormant account automation: flag users inactive >90 days, auto-suspend after warning

### Access Request Workflows
- [ ] Self-service access request: POST /api/v1/access-requests
  - Fields: requested_role, requested_tenant, justification, duration (optional)
- [ ] Approval queue: GET /api/v1/access-requests (admin view)
- [ ] Approve/deny: PATCH /api/v1/access-requests/:id
- [ ] Time-bound access: auto-revoke elevated role after approved duration expires
- [ ] Notifications: email/webhook to approver on request, to requester on decision
- [ ] Escalation: auto-escalate unanswered requests after configurable timeout

### Access Reviews & Certification Campaigns
- [ ] Campaign creation: POST /api/v1/access-reviews
- [ ] Review items: GET /api/v1/access-reviews/:id/items
- [ ] Certify/revoke per item: PATCH /api/v1/access-reviews/:id/items/:itemId
- [ ] Auto-revoke uncertified access after review deadline
- [ ] Scheduled reviews: recurring campaigns (quarterly, annually)

### Agentic Automation Hooks
- [ ] Webhook endpoints for lifecycle events
- [ ] Event bus integration point for external automation (n8n, Temporal, custom agents)
- [ ] AI agent compatibility: structured JSON on all lifecycle endpoints for LLM tool-use
- [ ] Idempotent operations: safe to retry any lifecycle action

## Machine Identity Lifecycle Governance

### API Key Lifecycle
- [ ] API key issuance tracked: who created, purpose, expiry
- [ ] Key classification: human-interactive vs. machine/service account vs. CI/CD
- [ ] Mandatory expiry: configurable per key type (default: 90 days machine, 365 service)
- [ ] Auto-rotation: notify before expiry, provide rotation endpoint
- [ ] POST /api/v1/keys/:id/rotate → new key, deprecate old with grace period
- [ ] Orphan key detection: unused >30 days flagged for review

### Workload Identity
- [ ] Workload identity federation (OIDC tokens from CI/CD, k8s service accounts)
- [ ] Short-lived token exchange: POST /api/v1/auth/token-exchange
- [ ] Bound tokens: scope to tenant + permissions + time window

### Machine Identity Inventory
- [ ] GET /api/v1/admin/machine-identities → all keys, service accounts, workload identities
- [ ] Classification: active/deprecated/expired/revoked
- [ ] Owner mapping: every machine identity linked to a responsible human
- [ ] Risk scoring: flag high-privilege identities without rotation schedule
`;

export function getIdentityGovernance(): string {
  return IDENTITY_GOVERNANCE;
}
