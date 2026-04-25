export const COMPLIANCE_CHECKLIST = `
# SaaS Compliance Automation Checklist

Run this checklist against a converted project to verify compliance readiness.

## 1. Tenant Data Isolation (CRITICAL)

### Automated Checks
- [ ] Every database model with user data has a tenant_id column
- [ ] Every SELECT query includes WHERE tenant_id = ?
- [ ] Every INSERT sets tenant_id from authenticated context
- [ ] Every UPDATE/DELETE scopes by tenant_id
- [ ] No raw SQL queries bypass tenant scoping
- [ ] Cross-tenant data access test passes (create data in tenant A, auth as tenant B, verify 404/403)

### How to Verify
1. Grep all query calls (ORM find/filter/where, raw SQL)
2. For each, confirm tenant_id is in the filter
3. Run isolation test script: create 2 tenants, attempt cross-access

## 2. Authentication & Authorization

### Automated Checks
- [ ] Passwords hashed with bcrypt (cost >= 12) or argon2
- [ ] JWT tokens expire (access: <=15min, refresh: <=7 days)
- [ ] Refresh tokens are single-use with rotation
- [ ] API keys are stored as SHA-256 hashes, never plaintext
- [ ] Failed login attempts are rate-limited (<=5/min per IP)
- [ ] Password reset tokens expire within 1 hour
- [ ] Email verification is required before full access
- [ ] Role-based access control enforced on all admin endpoints

### How to Verify
1. Inspect auth middleware for JWT expiry validation
2. Check password hashing config for cost factor
3. Test rate limiting on /auth/login endpoint
4. Verify admin routes reject non-admin tokens

## 3. Security Headers

### Automated Checks
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY or SAMEORIGIN
- [ ] Strict-Transport-Security: max-age>=31536000
- [ ] Content-Security-Policy present and restrictive
- [ ] Referrer-Policy: strict-origin-when-cross-origin or no-referrer
- [ ] Permissions-Policy restricts camera, microphone, geolocation
- [ ] No X-Powered-By header exposed

### How to Verify
1. curl -I https://your-app.com and check response headers
2. Run: curl -s -D- https://your-app.com -o /dev/null | grep -i "x-content-type\\|x-frame\\|strict-transport\\|content-security\\|referrer-policy\\|permissions-policy"

## 4. CORS Configuration

### Automated Checks
- [ ] Production CORS allows only specific origins (not *)
- [ ] Credentials mode is enabled
- [ ] Allowed methods are restricted (no wildcard)
- [ ] Allowed headers are restricted
- [ ] Preflight responses are cached (Access-Control-Max-Age)

### How to Verify
1. Send OPTIONS request with Origin header from unauthorized domain
2. Verify response does NOT include Access-Control-Allow-Origin

## 5. Rate Limiting

### Automated Checks
- [ ] Unauthenticated endpoints: <=20 req/min per IP
- [ ] Auth endpoints (login, register): <=5 req/min per IP
- [ ] Authenticated API: limits based on plan tier
- [ ] Rate limit headers present (X-RateLimit-Limit, X-RateLimit-Remaining)
- [ ] 429 response includes Retry-After header

### How to Verify
1. Send burst of requests to /api/v1/auth/login
2. Verify 429 after limit exceeded
3. Check response headers for rate limit info

## 6. Input Validation

### Automated Checks
- [ ] All request bodies validated with schema (Zod, Joi, Pydantic, etc.)
- [ ] No raw user input in SQL queries (parameterized only)
- [ ] HTML output is escaped (no XSS vectors)
- [ ] File uploads have size limits and type validation
- [ ] No mass assignment vulnerability (allowlists for accepted fields)
- [ ] URL parameters are validated and typed

### How to Verify
1. Send malformed JSON to POST endpoints — expect 400, not 500
2. Send SQL injection payloads — expect no data leak
3. Send XSS payloads — expect escaped output

## 7. Secrets Management

### Automated Checks
- [ ] No secrets in source code (grep for sk_, password=, secret=, key=)
- [ ] No .env file committed to git
- [ ] .gitignore includes .env, *.pem, *.key
- [ ] JWT_SECRET is >= 64 characters
- [ ] All secrets loaded from environment variables
- [ ] No secrets logged in application output

### How to Verify
1. grep -r "sk_\\|password=\\|secret=" --include="*.ts" --include="*.py" --include="*.go" src/
2. git log -- .env (should be empty)
3. Check logging middleware for secret redaction

## 8. GDPR / Privacy

### Automated Checks
- [ ] Data export endpoint exists (GET /api/v1/account/export)
- [ ] Account deletion endpoint exists (DELETE /api/v1/account)
- [ ] Deletion is soft-delete first, hard-delete after retention period
- [ ] Privacy policy page/route exists
- [ ] Cookie consent mechanism exists (if using cookies in frontend)
- [ ] Data processing records maintained
- [ ] User data encrypted at rest (database-level or application-level)

### How to Verify
1. Call GET /api/v1/account/export — verify all user data returned
2. Call DELETE /api/v1/account — verify account is deactivated
3. Check database for encryption at rest configuration

## 9. Logging & Audit Trail

### Automated Checks
- [ ] Authentication events logged (login, logout, failed attempts)
- [ ] Admin actions logged (tenant suspend, plan change, user role change)
- [ ] API access logged with tenant_id, user_id, endpoint, timestamp
- [ ] No PII or secrets in logs
- [ ] Log rotation configured
- [ ] Logs include request ID for tracing

### How to Verify
1. Trigger login → check logs for auth event
2. Trigger admin action → check logs for audit entry
3. grep logs for email addresses or passwords (should find none)

## 10. Infrastructure Security

### Automated Checks
- [ ] Docker container runs as non-root user
- [ ] No unnecessary ports exposed
- [ ] Database not exposed to public internet
- [ ] TLS/SSL configured for all public endpoints
- [ ] Database backups configured and tested
- [ ] Health check endpoints respond correctly
- [ ] Dependency vulnerability scan passes (npm audit, pip audit, etc.)

### How to Verify
1. docker inspect — check User field
2. nmap public IP — verify only expected ports open
3. Run npm audit / pip audit / go vuln check

## Compliance Score

After running all checks, calculate:
- CRITICAL (sections 1, 2, 7): Must be 100% — any failure is a blocker
- HIGH (sections 3, 4, 5, 6): Should be 100% before production
- MEDIUM (sections 8, 9): Should be addressed before handling EU user data
- LOW (section 10): Should be addressed before scaling

Report format:
| Section | Status | Score | Blockers |
|---------|--------|-------|----------|
| Tenant Isolation | PASS/FAIL | X/Y | List any failures |
| Auth & AuthZ | PASS/FAIL | X/Y | ... |
| ... | ... | ... | ... |
`;

export function getComplianceChecklist(): string {
  return COMPLIANCE_CHECKLIST;
}
