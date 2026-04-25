import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { z } from "zod";
import { validateKey, createKey, revokeKey, listKeys } from "./auth.js";
import { getFullGuide, getPhase } from "./content.js";
import { getComplianceChecklist } from "./compliance.js";
import { getIdentityGovernance } from "./identity.js";
import { getPlatformCapabilities } from "./platform.js";
import { getScaffoldGuide } from "./scaffold.js";
import { getConfigureGuide } from "./configure.js";
import { getDeployGuide } from "./deploy.js";
import { getDiagnoseGuide } from "./diagnose.js";
import { getModuleRegistry } from "./modules.js";

const app = express();
app.use(express.json());

const server = new McpServer({
  name: "saas-factory",
  version: "2.0.0",
});

// Tool: Get full conversion guide
server.tool(
  "get_conversion_guide",
  "Returns the complete OSS-to-SaaS conversion methodology. Use this when starting a new conversion — it provides all 6 phases (analysis, design, implementation, infrastructure, business, security) with decision tables, checklists, and framework-specific instructions.",
  {},
  async () => ({
    content: [{ type: "text", text: getFullGuide() }],
  })
);

// Tool: Get specific phase
server.tool(
  "get_conversion_phase",
  "Returns a specific phase of the conversion guide. Phase 1: Project Analysis, Phase 2: SaaS Architecture Design, Phase 3: Code Modifications, Phase 4: Infrastructure, Phase 5: Business Layer, Phase 6: Security & Compliance.",
  { phase: z.number().min(1).max(6).describe("Phase number (1-6)") },
  async ({ phase }) => ({
    content: [{ type: "text", text: getPhase(phase) }],
  })
);

// Tool: Get compliance checklist
server.tool(
  "get_compliance_checklist",
  "Returns the full SaaS compliance automation checklist including: tenant isolation, auth, security headers, CORS, rate limiting, input validation, secrets management, GDPR, logging/audit, infrastructure security, IAM/IdP integration (SAML, OIDC, SCIM), IGA (identity governance, access certification), PAM (privileged access), agentic user lifecycle management (access requests, reviews, automated provisioning), and machine identity lifecycle governance (API key rotation, service accounts, workload identity).",
  {},
  async () => ({
    content: [{ type: "text", text: getComplianceChecklist() }],
  })
);

// Tool: Get identity governance guide
server.tool(
  "get_identity_governance",
  "Returns the identity & access governance guide including: IAM/IdP integration (SAML 2.0, OIDC, SCIM 2.0), IGA (identity governance, access certification, separation of duties), PAM (privileged access management), agentic user lifecycle management (automated provisioning/deprovisioning, access request workflows, access reviews, certification campaigns), and machine identity lifecycle governance (API key lifecycle, workload identity, service accounts).",
  {},
  async () => ({
    content: [{ type: "text", text: getIdentityGovernance() }],
  })
);

// Tool: Get platform capabilities guide
server.tool(
  "get_platform_capabilities",
  "Returns the platform capabilities guide including: data ingestion module (bulk import/export, pipeline integration, webhook receiver), audit log system (event capture, append-only logs, hash chain integrity, SIEM integration), and changelog publishing (platform releases, tenant notifications, API changelog, activity feed).",
  {},
  async () => ({
    content: [{ type: "text", text: getPlatformCapabilities() }],
  })
);

// --- SaaS Factory tools (scaffold, configure, deploy, diagnose, modules) ---

server.tool(
  "get_scaffold_guide",
  "Returns the scaffold workflow for generating a complete SaaS project from scratch. Includes module selection menu (22 services across 5 layers), file generation templates (docker-compose.yml, .env, Caddyfile, Makefile, scripts, migrations), and post-scaffold guidance.",
  {},
  async () => ({
    content: [{ type: "text", text: getScaffoldGuide() }],
  })
);

server.tool(
  "get_configure_guide",
  "Returns the service configuration guide for setting up services via MCP tools after the stack is running. Covers 8 services: Lago (billing plans), n8n (workflow templates), NocoDB (admin dashboard), GlitchTip (error tracking), Uptime Kuma (monitors), Matomo (analytics), Mautic (email marketing), Stalwart (mail server). Lists all MCP tool names for each service.",
  {},
  async () => ({
    content: [{ type: "text", text: getConfigureGuide() }],
  })
);

server.tool(
  "get_deploy_guide",
  "Returns the deployment guide for pushing the SaaS stack to production. Covers Coolify deployment and direct Docker Compose deployment. Includes pre-flight checklist, resource requirements, DNS configuration table, firewall setup, and post-deploy verification steps.",
  {},
  async () => ({
    content: [{ type: "text", text: getDeployGuide() }],
  })
);

server.tool(
  "get_diagnose_guide",
  "Returns the troubleshooting and health check guide. Includes systematic debugging steps, common issues table (15+ known problems with fixes), MCP-assisted diagnosis via Uptime Kuma/GlitchTip/n8n/Lago, and emergency procedures for service failures, database corruption, and server reboots.",
  {},
  async () => ({
    content: [{ type: "text", text: getDiagnoseGuide() }],
  })
);

server.tool(
  "get_module_registry",
  "Returns the complete 22-service module registry with dependencies, subdomains, health URLs, layer groupings (essential/core/ops/growth/ai), resource requirements, Docker Compose profiles, multi-tenancy architecture diagram, and 14 AI MCP tools (Ollama, Langflow, Claude Agent, Langfuse).",
  {},
  async () => ({
    content: [{ type: "text", text: getModuleRegistry() }],
  })
);

// Auth middleware for MCP endpoint
function authenticateRequest(
  req: express.Request,
  res: express.Response
): boolean {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    res.status(401).json({ error: "Missing or invalid Authorization header" });
    return false;
  }

  const token = authHeader.slice(7);
  const result = validateKey(token);
  if (!result.valid) {
    res.status(403).json({ error: "Invalid or revoked API key" });
    return false;
  }

  return true;
}

// --- Admin API for key management ---
// Protected by ADMIN_SECRET env var

function authenticateAdmin(
  req: express.Request,
  res: express.Response
): boolean {
  const adminSecret = process.env.ADMIN_SECRET;
  if (!adminSecret) {
    res.status(503).json({ error: "ADMIN_SECRET not configured" });
    return false;
  }
  const authHeader = req.headers.authorization;
  if (authHeader !== `Bearer ${adminSecret}`) {
    res.status(403).json({ error: "Invalid admin credentials" });
    return false;
  }
  return true;
}

// List all API keys
app.get("/api/v1/keys", (req, res) => {
  if (!authenticateAdmin(req, res)) return;
  res.json({ keys: listKeys() });
});

// Create a new API key
app.post("/api/v1/keys", (req, res) => {
  if (!authenticateAdmin(req, res)) return;
  const { name } = req.body;
  if (!name || typeof name !== "string") {
    res.status(400).json({ error: "name is required" });
    return;
  }
  const result = createKey(name);
  res.status(201).json(result);
});

// Revoke an API key
app.delete("/api/v1/keys/:id", (req, res) => {
  if (!authenticateAdmin(req, res)) return;
  const revoked = revokeKey(req.params.id);
  if (!revoked) {
    res.status(404).json({ error: "Key not found" });
    return;
  }
  res.json({ revoked: true, id: req.params.id });
});

// Validate an API key (check if active)
app.post("/api/v1/keys/validate", (req, res) => {
  if (!authenticateAdmin(req, res)) return;
  const { key } = req.body;
  if (!key || typeof key !== "string") {
    res.status(400).json({ error: "key is required" });
    return;
  }
  res.json(validateKey(key));
});

// --- Health ---

app.get("/healthz", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// MCP endpoint with auth
app.post("/mcp", async (req, res) => {
  if (!authenticateRequest(req, res)) return;

  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });

  res.on("close", () => {
    transport.close();
  });

  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

// Handle GET and DELETE for MCP protocol
app.get("/mcp", async (req, res) => {
  if (!authenticateRequest(req, res)) return;
  res.writeHead(405).end(JSON.stringify({ error: "Method not allowed" }));
});

app.delete("/mcp", async (req, res) => {
  if (!authenticateRequest(req, res)) return;
  res.writeHead(405).end(JSON.stringify({ error: "Method not allowed" }));
});

const PORT = process.env.PORT || 3100;

app.listen(PORT, () => {
  console.log(`saas-factory MCP server running on port ${PORT}`);
  console.log(`MCP endpoint: http://localhost:${PORT}/mcp`);
  console.log(`Health check: http://localhost:${PORT}/healthz`);
});
