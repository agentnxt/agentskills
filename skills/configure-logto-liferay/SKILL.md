---
name: configure-logto-liferay
description: >
  Configures Logto as an OpenID Connect (OIDC) identity provider for Liferay DXP/CE
  single sign-on. Walks through Logto application setup, Liferay OIDC provider
  configuration, user attribute mapping, and sign-in widget integration.
  Trigger on: "configure Logto for Liferay", "set up Logto SSO on Liferay",
  "Liferay OpenID Connect with Logto", "Logto sign-in for Liferay",
  "add Logto authentication to Liferay", "OIDC login Liferay Logto".
---

# Configure Logto Sign-In for Liferay

Sets up [Logto](https://logto.io) as the OpenID Connect identity provider for
[Liferay DXP / CE](https://www.liferay.com), enabling SSO login, automatic user
provisioning, and attribute mapping.

---

## Prerequisites

Before starting, confirm the user has:

| Requirement | Details |
|---|---|
| **Logto instance** | Cloud (`https://<tenant>.logto.app`) or self-hosted (`https://logto.example.com`) |
| **Logto admin access** | Ability to create Applications in the Logto Console |
| **Liferay DXP 7.4+ or CE 7.4+** | Earlier versions lack the OIDC provider UI — manual `osgi/configs` required |
| **Liferay admin access** | Omni-admin or portal-level admin role |
| **HTTPS on both sides** | Required for secure redirect URIs |

Ask the user for:
1. Logto instance URL (cloud or self-hosted)
2. Liferay portal URL (e.g., `https://liferay.example.com`)
3. Desired user-matching strategy: **email** (default) or **UUID/sub**

---

## Step 1 — Create a Logto Application

In the **Logto Console** (`/applications`):

1. Click **Create Application**
2. Select **Traditional Web Application**
3. Set the application name: `Liferay Portal` (or as the user prefers)
4. After creation, note these values from the application detail page:

| Field | Where to find | Example |
|---|---|---|
| **App ID** (Client ID) | Application details → App ID | `a1b2c3d4e5f6` |
| **App Secret** (Client Secret) | Application details → App Secret | `secret_xxxxx` |
| **Issuer / OIDC Discovery** | Endpoint tab or `https://<tenant>.logto.app/oidc/.well-known/openid-configuration` | — |

5. Configure **Redirect URIs** — add:
   ```
   https://<LIFERAY_HOST>/c/portal/login/openid_connect
   ```
6. Configure **Post Sign-out Redirect URIs** — add:
   ```
   https://<LIFERAY_HOST>/c/portal/logout
   ```
7. On the **Permissions** (scopes) section, ensure these are enabled:
   - `openid`
   - `profile`
   - `email`

8. **Save** the application.

---

## Step 2 — Gather Logto OIDC Endpoints

Fetch the well-known configuration:

```
GET https://<LOGTO_HOST>/oidc/.well-known/openid-configuration
```

Extract and record:

| Endpoint | JSON key | Typical value |
|---|---|---|
| **Authorization** | `authorization_endpoint` | `https://<LOGTO_HOST>/oidc/auth` |
| **Token** | `token_endpoint` | `https://<LOGTO_HOST>/oidc/token` |
| **UserInfo** | `userinfo_endpoint` | `https://<LOGTO_HOST>/oidc/me` |
| **End Session** | `end_session_endpoint` | `https://<LOGTO_HOST>/oidc/session/end` |
| **JWKS** | `jwks_uri` | `https://<LOGTO_HOST>/oidc/jwks` |
| **Issuer** | `issuer` | `https://<LOGTO_HOST>/oidc` |

---

## Step 3 — Configure Liferay OIDC Provider

### Option A: Liferay Admin UI (DXP 7.4+ / CE 7.4+)

1. Go to **Control Panel → Instance Settings → Security → SSO**
2. Click **OpenID Connect Provider**
3. Click **Add** to create a new provider with these values:

| Liferay Field | Value |
|---|---|
| **Provider Name** | `Logto` |
| **OpenID Connect Client ID** | `<App ID from Step 1>` |
| **OpenID Connect Client Secret** | `<App Secret from Step 1>` |
| **Discovery Endpoint** | `https://<LOGTO_HOST>/oidc/.well-known/openid-configuration` |
| **Discovery Document Use** | Use discovery document |
| **Authorization Endpoint** | (auto-populated from discovery, or paste from Step 2) |
| **Token Endpoint** | (auto-populated from discovery, or paste from Step 2) |
| **UserInfo Endpoint** | (auto-populated from discovery, or paste from Step 2) |
| **Scopes** | `openid profile email` |
| **OpenID Connect User Info Processor Implementation** | Default or custom (see Step 4) |

4. **Save** the provider.
5. Go to **Instance Settings → Security → SSO → OpenID Connect** (the top-level toggle)
6. Check **Enabled** to activate OIDC login on the Liferay sign-in page.

### Option B: OSGi Config File (headless / CI/CD)

Create the file:
`osgi/configs/com.liferay.portal.security.sso.openid.connect.internal.configuration.OpenIdConnectProviderConfiguration-logto.config`

```properties
providerName="Logto"
openIdConnectClientId="<APP_ID>"
openIdConnectClientSecret="<APP_SECRET>"
discoveryEndPoint="https://<LOGTO_HOST>/oidc/.well-known/openid-configuration"
scopes="openid profile email"
```

Enable OIDC globally in:
`osgi/configs/com.liferay.portal.security.sso.openid.connect.configuration.OpenIdConnectConfiguration.config`

```properties
enabled=B"true"
```

Restart the Liferay module or the portal for config pickup.

---

## Step 4 — User Attribute Mapping

Logto returns these standard OIDC claims. Map them to Liferay user fields:

| Logto Claim | Liferay User Field | Notes |
|---|---|---|
| `sub` | `openId` | Unique user ID in Logto |
| `email` | `emailAddress` | Primary matching key (default) |
| `email_verified` | — | Check before trusting email |
| `name` | `fullName` | Display name |
| `given_name` | `firstName` | If Logto custom claims configured |
| `family_name` | `lastName` | If Logto custom claims configured |
| `picture` | `portraitURL` | Profile image URL |

### Custom Claim Mapping (if needed)

If the user needs `firstName` / `lastName` split (Logto returns `name` by default), guide them to:

1. In Logto Console → **User Management → User Profile**, configure custom profile fields, OR
2. In Logto, create a **Custom JWT** claim via **Machine-to-Machine roles** to include `given_name` and `family_name`, OR
3. In Liferay, implement a custom `OpenIdConnectUserInfoProcessor` that splits the `name` claim:

```java
@Component(
    property = "open.id.connect.user.info.processor.name=logto-name-splitter",
    service = OpenIdConnectUserInfoProcessor.class
)
public class LogtoUserInfoProcessor implements OpenIdConnectUserInfoProcessor {

    @Override
    public String process(
        long companyId, long userId, UserInfo userInfo) throws Exception {

        String fullName = userInfo.getName();
        if (fullName != null && fullName.contains(" ")) {
            String[] parts = fullName.split(" ", 2);
            // Set firstName = parts[0], lastName = parts[1]
            // via UserLocalServiceUtil or custom logic
        }
        return null; // return null to use default processing
    }
}
```

---

## Step 5 — Test the Integration

Walk the user through this verification checklist:

1. **Open Liferay sign-in page** — confirm the **Logto** provider button appears
2. **Click the Logto button** — verify redirect to Logto login screen
3. **Sign in with a Logto user** — verify redirect back to Liferay
4. **Check user creation** — in Liferay Control Panel → Users, confirm the user was auto-provisioned
5. **Check attribute mapping** — verify email, name, and profile image populated correctly
6. **Test sign-out** — confirm logout from Liferay also ends the Logto session (SLO)
7. **Test error cases**:
   - User with unverified email in Logto
   - User that already exists in Liferay with the same email (merge behavior)

---

## Step 6 — Production Hardening

| Setting | Recommendation |
|---|---|
| **Token expiration** | Set Logto access token TTL to 3600s (1 hour) |
| **Refresh tokens** | Enable in Logto app settings for persistent sessions |
| **Logto roles → Liferay roles** | Map via custom `OpenIdConnectUserInfoProcessor` using Logto `roles` claim |
| **MFA** | Enable MFA in Logto Console → Sign-in Experience for all users |
| **Branding** | Customize the Logto sign-in page (logo, colors) to match the Liferay portal branding |
| **Session management** | Set Liferay `session.timeout` ≤ Logto token expiry to avoid stale sessions |
| **CORS** | If Logto is self-hosted, ensure Liferay's domain is in Logto's allowed origins |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Invalid redirect_uri" on Logto | Redirect URI mismatch | Ensure `https://<LIFERAY_HOST>/c/portal/login/openid_connect` is exactly listed in Logto app settings |
| Liferay shows "OpenID Connect provider not found" | OIDC not enabled or provider not saved | Check Instance Settings → SSO → OpenID Connect is **Enabled** |
| User created but no email | `email` scope missing or email unverified in Logto | Add `email` scope; in Logto, ensure users have verified emails |
| "JWT signature verification failed" | Clock skew or wrong JWKS | Sync server clocks (NTP); verify discovery endpoint returns correct `jwks_uri` |
| Logout doesn't end Logto session | Post-logout redirect URI not configured | Add Liferay logout URL to Logto's **Post Sign-out Redirect URIs** |
| 403 after successful auth | User exists in Liferay but is deactivated | Reactivate user in Liferay or configure auto-activation in the UserInfoProcessor |

---

## Architecture Summary

```
┌──────────────┐     OIDC Auth Code Flow     ┌──────────────┐
│              │  ──── 1. /authorize ──────►  │              │
│   Liferay    │                              │    Logto     │
│   Portal     │  ◄─── 2. auth code ────────  │    IdP       │
│              │  ──── 3. /token ───────────►  │              │
│              │  ◄─── 4. id_token + access ─  │              │
│              │  ──── 5. /userinfo ────────►  │              │
│              │  ◄─── 6. user claims ───────  │              │
└──────────────┘                              └──────────────┘
       │                                             │
       ▼                                             ▼
  User provisioned                           User authenticated
  in Liferay DB                              via Logto credentials
```

**Flow:** Liferay redirects to Logto → user authenticates → Logto returns auth code → Liferay exchanges code for tokens → Liferay fetches user info → user is provisioned/matched in Liferay → session established.
