# saas-factory

Unified SaaS factory — scaffolds, converts, configures, deploys, and diagnoses SaaS products. Combines the OSS-to-SaaS conversion engine with the Autonomyx Fast SaaS Toolkit (22 pre-wired services).

Available as both a **local Claude Code skill** (`/saas-factory`) and an **auth-gated MCP server** for team access.

## 5 Modes

| Mode | What it does |
|------|-------------|
| **Scaffold** | Generate a complete SaaS project from scratch (22-service Docker Compose stack) |
| **Configure** | Set up services via MCP tools (Lago, n8n, NocoDB, GlitchTip, Uptime Kuma, Matomo, Mautic, Stalwart) |
| **Convert** | Convert any OSS project to multi-tenant SaaS (6-phase methodology, framework-agnostic) |
| **Deploy** | Deploy via Coolify or Docker Compose with dependency ordering |
| **Diagnose** | Health check + troubleshooting with common issues table |

## 10 MCP Tools

| Tool | Description |
|------|-------------|
| `get_conversion_guide` | Full 6-phase OSS-to-SaaS conversion methodology |
| `get_conversion_phase` | Specific phase (1-6) of the conversion guide |
| `get_compliance_checklist` | Tenant isolation, auth, security, GDPR checklist |
| `get_identity_governance` | IAM/IdP, IGA, PAM, agentic lifecycle, machine identity |
| `get_platform_capabilities` | Data ingestion, audit log, changelog publishing |
| `get_scaffold_guide` | Scaffold workflow + module selection + file templates |
| `get_configure_guide` | Service configuration via MCP tools (8 services) |
| `get_deploy_guide` | Deployment workflow + pre-flight + DNS + firewall |
| `get_diagnose_guide` | Troubleshooting guide + common issues + emergency procedures |
| `get_module_registry` | 22-service registry with deps, health URLs, AI tools |

## Structure

```
├── SKILL.md                  # Local skill (install to ~/.claude/skills/saas-factory/)
└── mcp-server/               # Auth-gated MCP server
    ├── src/
    │   ├── index.ts           # MCP server (10 tools) + admin REST API
    │   ├── auth.ts            # API key management (create, revoke, validate)
    │   ├── content.ts         # Conversion methodology (6 phases)
    │   ├── compliance.ts      # Security/GDPR compliance checklist
    │   ├── identity.ts        # IAM/IdP/IGA/PAM/agentic lifecycle
    │   ├── platform.ts        # Data ingestion, audit log, changelog
    │   ├── scaffold.ts        # Scaffold workflow + module menu
    │   ├── configure.ts       # Service configuration via MCP tools
    │   ├── deploy.ts          # Deployment workflow + pre-flight
    │   ├── diagnose.ts        # Troubleshooting + common issues
    │   ├── modules.ts         # 22-service module registry
    │   └── keys.ts            # CLI for key management
    ├── Dockerfile
    └── docker-compose.yml
```

## Option A: Local Skill

```bash
mkdir -p ~/.claude/skills/saas-factory
cp SKILL.md ~/.claude/skills/saas-factory/SKILL.md
```

Then run `/saas-factory` in any project directory.

## Option B: MCP Server (team access with key management)

```bash
cd mcp-server
docker compose up -d --build
```

### Manage API keys

```bash
npm run keys -- create "alice@company.com"   # Create key
npm run keys -- list                          # List all keys
npm run keys -- revoke <key-id>              # Revoke (instant)
```

### Team members connect

```json
{
  "mcpServers": {
    "saas-factory": {
      "type": "streamable-http",
      "url": "https://your-server/mcp",
      "headers": {
        "Authorization": "Bearer scs_<api-key>"
      }
    }
  }
}
```

## License

Proprietary. All rights reserved.
