# Provider Connectors Reference

All connectors follow the same contract: `resolve(identifier, token?) → IdentityNode | None`

---

## Table of Contents
1. [Google](#google)
2. [GitHub](#github)
3. [Microsoft / Entra ID / Azure AD](#microsoft)
4. [Apple](#apple)
5. [LinkedIn](#linkedin)
6. [Twitter / X](#twitter)
7. [Logto (Autonomyx native)](#logto)
8. [Okta](#okta)
9. [Auth0](#auth0)
10. [Ping Identity](#ping)
11. [Keycloak](#keycloak)
12. [Custom / Generic OIDC](#custom)

---

## 1. Google {#google}

**Scopes required:** `openid email profile`
**Endpoint:** `GET https://openidconnect.googleapis.com/v1/userinfo`
**Auth:** `Authorization: Bearer {access_token}`

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `sub` | `provider_sub` |
| `email` | `email` |
| `email_verified` | `email_verified` |
| `name` | `display_name` |
| `picture` | `profile_photo_url` |
| `hd` | `org` (Google Workspace domain) |

**Notes:**
- `hd` is set only for Workspace accounts — map to `org`
- Phone not available via userinfo; requires People API (`people.get` with `phoneNumbers`)
- Token introspect: `https://oauth2.googleapis.com/tokeninfo?access_token=X`

---

## 2. GitHub {#github}

**Scopes required:** `read:user user:email`
**Endpoints:**
- `GET https://api.github.com/user` — primary profile
- `GET https://api.github.com/user/emails` — verified email list

**Auth:** `Authorization: Bearer {token}` or `token {token}`

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `id` (integer) | `provider_sub` (stringify) |
| primary verified email from `/user/emails` | `email` |
| `login` | `username` |
| `name` | `display_name` |
| `avatar_url` | `profile_photo_url` |
| `bio` | `bio` |
| `company` | `org` |
| `location` | `location` |

**Notes:**
- Use `/user/emails` to find `verified: true` + `primary: true` email
- GitHub does not expose phone numbers

---

## 3. Microsoft / Entra ID / Azure AD {#microsoft}

**Scopes required:** `openid email profile User.Read`
**Endpoint:** `GET https://graph.microsoft.com/v1.0/me`

**Auth:** `Authorization: Bearer {access_token}`

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `id` | `provider_sub` |
| `mail` or `userPrincipalName` | `email` |
| `displayName` | `display_name` |
| `givenName` + `surname` | fallback display_name |
| `jobTitle` | `bio` (reuse) |
| `companyName` | `org` |
| `officeLocation` | `location` |
| `mobilePhone` | `phone` |

**Photo endpoint:** `GET https://graph.microsoft.com/v1.0/me/photo/$value` → binary; store as data URI or upload to CDN, store URL only.

**Notes:**
- `userPrincipalName` is preferred for corporate accounts (`user@company.com`)
- For personal Microsoft accounts, `mail` is used
- Azure AD tenant can be resolved from JWT `tid` claim

---

## 4. Apple {#apple}

**Scopes required:** `name email`
**Note:** Apple only returns `name` and `email` on **first** authorization. Subsequent tokens return only `sub`.

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `sub` | `provider_sub` |
| `email` | `email` |
| `email_verified` (string "true") | `email_verified` |
| `is_private_email` | flag in `raw_profile` |

**Notes:**
- Private Relay emails (`@privaterelay.appleid.com`) cannot be used for cross-provider linkage
- Store `is_private_email: true` in raw_profile and skip email-based linkage for these
- No profile photo, bio, org, location available

---

## 5. LinkedIn {#linkedin}

**Scopes required:** `openid profile email`
**Endpoint:** `GET https://api.linkedin.com/v2/userinfo` (OpenID Connect)

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `sub` | `provider_sub` |
| `email` | `email` |
| `email_verified` | `email_verified` |
| `name` | `display_name` |
| `given_name` + `family_name` | fallback display_name |
| `picture` | `profile_photo_url` |

**Notes:**
- `locale`, `headline` available via `/v2/me` with `r_liteprofile` scope
- Organization / employer not in OpenID endpoint; requires `r_organization_social` scope (deprecated for most apps)
- Rate limits: 500 calls/day per app

---

## 6. Twitter / X {#twitter}

**Scopes required:** `tweet.read users.read`
**Endpoint:** `GET https://api.twitter.com/2/users/me?user.fields=name,username,description,profile_image_url,location,verified`

**Auth:** OAuth 2.0 Bearer token

**Field mapping:**
| Provider field | IdentityNode field |
|---|---|
| `id` | `provider_sub` |
| `username` | `username` |
| `name` | `display_name` |
| `description` | `bio` |
| `profile_image_url` | `profile_photo_url` |
| `location` | `location` |

**Notes:**
- Email not available via v2 API (requires legacy v1.1 with special approval)
- `verified` (blue check) stored in `raw_profile`
- No phone available

---

## 7. Logto (Autonomyx native) {#logto}

Logto is the primary IdP for Autonomyx. It federates all above providers and stores the linked account map internally.

**Token introspect:** `POST https://{logto_domain}/oidc/token/introspection`
**User detail:** `GET https://{logto_domain}/api/users/{userId}` (Management API, requires `all` scope)

**Field mapping:**
| Logto field | IdentityNode field |
|---|---|
| `sub` / `id` | `provider_sub` |
| `primaryEmail` | `email` |
| `primaryPhone` | `phone` |
| `username` | `username` |
| `name` | `display_name` |
| `avatar` | `profile_photo_url` |
| `identities` | → expand to linked account stubs per provider |

**Key capability:** `identities` object in Logto user record contains all federated provider `sub` values. This is the **fastest path** to cross-provider linkage — if Logto has the user, iterate `identities` directly.

**Env vars needed:**
```
LOGTO_DOMAIN=your.logto.domain
LOGTO_M2M_APP_ID=...
LOGTO_M2M_APP_SECRET=...
```

---

## 8. Okta {#okta}

**Endpoint:** `GET https://{okta_domain}/api/v1/users/{userId}`
**Auth:** `Authorization: SSWS {api_token}` or OAuth 2.0 with `okta.users.read` scope

**Field mapping:**
| Okta field | IdentityNode field |
|---|---|
| `id` | `provider_sub` |
| `profile.email` | `email` |
| `profile.mobilePhone` | `phone` |
| `profile.login` | `username` |
| `profile.displayName` | `display_name` |
| `profile.organization` | `org` |

---

## 9. Auth0 {#auth0}

**Endpoint:** `GET https://{auth0_domain}/api/v2/users/{user_id}`
**Auth:** Management API token with `read:users` scope

**Field mapping:**
| Auth0 field | IdentityNode field |
|---|---|
| `user_id` | `provider_sub` |
| `email` | `email` |
| `email_verified` | `email_verified` |
| `phone_number` | `phone` |
| `username` | `username` |
| `name` | `display_name` |
| `picture` | `profile_photo_url` |
| `identities` | → expand to linked account stubs |

**Notes:**
- Auth0 `identities` array works similarly to Logto — iterate for cross-provider links
- `user_id` format: `provider|sub` (e.g. `google-oauth2|103xxx`)

---

## 10. Ping Identity {#ping}

**Endpoint:** `GET https://api.pingone.com/v1/environments/{envId}/users/{userId}`
**Auth:** Worker app access token with `p1:read:user` scope

**Field mapping:**
| Ping field | IdentityNode field |
|---|---|
| `id` | `provider_sub` |
| `email.address` | `email` |
| `mobilePhone` | `phone` |
| `username` | `username` |
| `name.formatted` | `display_name` |

---

## 11. Keycloak {#keycloak}

**Endpoints:**
- OIDC introspect: `POST {realm_url}/protocol/openid-connect/token/introspect`
- Admin: `GET {admin_url}/admin/realms/{realm}/users/{id}`

**Field mapping:**
| Keycloak field | IdentityNode field |
|---|---|
| `sub` / `id` | `provider_sub` |
| `email` | `email` |
| `emailVerified` | `email_verified` |
| `username` | `username` |
| `firstName` + `lastName` | `display_name` |
| `attributes.phone` | `phone` |

**Notes:**
- Keycloak custom attributes (e.g. `phone`, `org`) stored in `attributes` map
- Federated identity links available via `GET /admin/realms/{realm}/users/{id}/federated-identity`

---

## 12. Custom / Generic OIDC {#custom}

For any provider implementing OIDC Discovery:

1. Fetch `{issuer}/.well-known/openid-configuration`
2. Hit `userinfo_endpoint` with `Authorization: Bearer {token}`
3. Map `sub` → `provider_sub`, `email` → `email`, `name` → `display_name`
4. Store full response in `raw_profile_enc`

Register via `identity_provider` table with `type: "custom"` and `issuer_url`.

---

## Connector Base Contract (Python)

```python
# scripts/connectors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class IdentityNode:
    provider: str
    provider_sub: str
    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    org: Optional[str] = None
    location: Optional[str] = None
    raw_profile: dict = None
    linked_account_stubs: list[dict] = None  # [{provider, provider_sub}]

class BaseConnector(ABC):
    provider_name: str

    @abstractmethod
    async def resolve(self, identifier: str, token: Optional[str] = None) -> Optional[IdentityNode]:
        """Resolve an identifier to an IdentityNode. Return None if not found."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider API is reachable."""
        ...
```
