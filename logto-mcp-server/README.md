# Logto MCP Server

A fully-featured [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes the complete **Logto Management API** and **Accounts API** as MCP tools — built for self-hosted Logto instances.

## Features

- **120+ MCP tools** covering every endpoint group in Logto's API
- Auto-refreshing M2M token management (no manual token rotation)
- Optional Accounts API support (end-user self-service tools)
- Clean error messages with HTTP status codes
- Works with Claude Desktop, Claude Code, and any MCP-compatible client

## Tool Groups

| Group | Tools |
|---|---|
| Users | list, get, create, update, delete, suspend, password, roles, identities, organizations, MFA, logs, custom data |
| Applications | list, create, get, update, delete, secrets, roles, sign-in experience, consent scopes, custom domains |
| Organizations | list, create, get, update, delete, users, user roles, user scopes, applications, application roles |
| Organization Roles | full CRUD + scope assignment (org scopes + resource scopes) |
| Organization Scopes | full CRUD |
| Organization Invitations | list, create, get, delete, update status, resend |
| API Resources & Scopes | full CRUD |
| Roles | full CRUD + scope/user/application assignment |
| Connectors | list, create, get, update, delete, test, factories |
| Enterprise SSO | list, create, get, update, delete, providers |
| Webhooks (Hooks) | list, create, get, update, delete, test, recent logs, signing key |
| Sign-in Experience | get, update |
| Configs | admin console, OIDC keys (rotate/delete), JWT customizers, ID token config |
| Audit Logs | list, get |
| Domains | list, create, get, delete |
| Dashboard | total users, new users, active users |
| Email Templates | list, get, update, delete, replace bulk |
| Custom Phrases (i18n) | list, get, upsert, delete |
| Custom Profile Fields | list, create, get, update, delete |
| One-Time Tokens | list, create, get, delete, verify, update status |
| Captcha Provider | get, update, delete |
| Account Center | get, update |
| **Accounts API** | profile, other profile, password, email, phone, identities, social tokens, MFA settings, MFA verifications, TOTP, backup codes |

## Setup

### 1. Create a Machine-to-Machine App in Logto

1. Go to **Logto Console → Applications → Create application**
2. Choose **Machine-to-Machine**
3. After creation, go to **Permissions** tab
4. Add the **Logto Management API** resource → select `all` scope
5. Copy the **App ID** and **App Secret**

### 2. Install & Build

```bash
npm install
npm run build
```

### 3. Run

```bash
LOGTO_ENDPOINT=https://your-logto.example.com \
LOGTO_APP_ID=your-m2m-app-id \
LOGTO_APP_SECRET=your-m2m-app-secret \
node dist/index.js
```

## Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "logto": {
      "command": "node",
      "args": ["/absolute/path/to/logto-mcp-server/dist/index.js"],
      "env": {
        "LOGTO_ENDPOINT": "https://your-logto.example.com",
        "LOGTO_APP_ID": "your-m2m-app-id",
        "LOGTO_APP_SECRET": "your-m2m-app-secret"
      }
    }
  }
}
```

## Accounts API (Optional)

The Accounts API tools (`account_*`) let you operate in the context of a specific signed-in user. To enable:

1. Obtain an access token for a user (via your app's sign-in flow)
2. Set `LOGTO_ACCOUNTS_TOKEN=<the_bearer_token>` in the environment

The token must have the audience `https://your-logto.example.com/api/my-account`.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `LOGTO_ENDPOINT` | ✅ | Your Logto instance URL (no trailing slash) |
| `LOGTO_APP_ID` | ✅ | M2M application App ID |
| `LOGTO_APP_SECRET` | ✅ | M2M application App Secret |
| `LOGTO_ACCOUNTS_TOKEN` | ❌ | End-user Bearer token for Accounts API tools |
