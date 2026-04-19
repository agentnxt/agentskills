# Microsoft Entra ID — Authentication & Identity Reference

Source: https://learn.microsoft.com/en-us/entra/

## Core Concepts

- **Tenant** — Your organization's dedicated Entra ID directory
- **App Registration** — Registers your app with Entra ID (gets client_id)
- **Service Principal** — The app's identity within a tenant
- **Managed Identity** — Auto-managed credential for Azure resources (no secrets needed)
- **Enterprise Application** — The service principal + SSO config visible to admins

## OAuth 2.0 Flows

### 1. Authorization Code + PKCE (Web & SPA)
Best for: User-facing web apps, SPAs, mobile apps
```
Step 1 — Redirect user to:
GET https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
  ?client_id={client_id}
  &response_type=code
  &redirect_uri={redirect_uri}
  &scope=openid profile email offline_access User.Read
  &code_challenge={pkce_challenge}
  &code_challenge_method=S256

Step 2 — Exchange code for tokens:
POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
  grant_type=authorization_code
  &code={auth_code}
  &redirect_uri={redirect_uri}
  &client_id={client_id}
  &code_verifier={pkce_verifier}
```

### 2. Client Credentials (Daemon / Service-to-Service)
Best for: Background jobs, APIs, no user interaction
```
POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
  grant_type=client_credentials
  &client_id={client_id}
  &client_secret={client_secret}  ← or certificate (preferred)
  &scope=https://graph.microsoft.com/.default
```
⚠️ Use certificates over secrets in production. Use Managed Identity where possible.

### 3. On-Behalf-Of (OBO)
Best for: API calling downstream API on behalf of user
```
POST /oauth2/v2.0/token
  grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
  &assertion={user_access_token}
  &client_id={api_client_id}
  &client_secret={api_secret}
  &scope=https://graph.microsoft.com/Mail.Read
  &requested_token_use=on_behalf_of
```

### 4. Device Code Flow
Best for: CLI tools, IoT, devices without browsers
```
Step 1: POST /oauth2/v2.0/devicecode → returns user_code + device_code
Step 2: User visits https://microsoft.com/devicelogin and enters user_code
Step 3: Poll POST /oauth2/v2.0/token until approved
```

## MSAL Code Samples

### Python (MSAL)
```python
import msal

app = msal.ConfidentialClientApplication(
    client_id="...",
    authority="https://login.microsoftonline.com/{tenant}",
    client_credential="client_secret_or_cert"
)

# Client credentials
result = app.acquire_token_for_client(
    scopes=["https://graph.microsoft.com/.default"]
)
access_token = result["access_token"]
```

### JavaScript (MSAL Browser)
```javascript
import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: "...",
    authority: "https://login.microsoftonline.com/{tenant}",
    redirectUri: "https://yourapp.com/callback"
  }
};

const msalInstance = new PublicClientApplication(msalConfig);
const loginRequest = { scopes: ["User.Read", "Mail.Read"] };

const result = await msalInstance.loginPopup(loginRequest);
```

### C# (.NET)
```csharp
var app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithTenantId(tenantId)
    .WithClientSecret(clientSecret) // or .WithCertificate()
    .Build();

var result = await app.AcquireTokenForClient(
    new[] { "https://graph.microsoft.com/.default" })
    .ExecuteAsync();
```

## Managed Identity (Recommended for Azure Resources)

No secrets, no rotation, automatic:
```python
# Python - works on any Azure compute (App Service, Functions, AKS, VM)
from azure.identity import DefaultAzureCredential
from msgraph import GraphServiceClient

credential = DefaultAzureCredential()
client = GraphServiceClient(credential)
```

```csharp
// C# - same pattern
var credential = new DefaultAzureCredential();
var graphClient = new GraphServiceClient(credential);
```

## Conditional Access & MFA

Key policies to know:
- **Require MFA** — For all users or specific groups/apps
- **Require compliant device** — Intune-managed devices only
- **Sign-in risk policy** — Block/challenge risky sign-ins (needs P2)
- **Named Locations** — Block/allow by IP range or country

Conditional Access requires **Entra ID P1 or P2**.

## Token Structure (JWT)
Tokens are JWTs. Key claims:
- `oid` — Object ID (unique, stable user identifier — use this, not UPN)
- `sub` — Subject (app-specific user identifier)
- `upn` — User Principal Name (email)
- `tid` — Tenant ID
- `scp` — Scopes (delegated permissions)
- `roles` — App roles (application permissions)
- `exp` — Expiry timestamp

Decode tokens at: https://jwt.ms

## App Roles (Authorization)
Define roles in app manifest:
```json
"appRoles": [
  {
    "displayName": "Admin",
    "id": "guid",
    "isEnabled": true,
    "value": "Admin",
    "allowedMemberTypes": ["User", "Application"]
  }
]
```
Assign roles to users/groups in Enterprise Applications → App roles.
Roles appear in `roles` claim in the token.

## Key Entra ID Admin Portals
- Entra admin center: https://entra.microsoft.com
- Azure portal (Entra blade): https://portal.azure.com/#view/Microsoft_AAD_IAM
- App registrations: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps
