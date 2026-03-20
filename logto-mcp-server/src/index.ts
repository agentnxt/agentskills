#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { getManagementClient, getAccountsClient, LogtoConfig } from "./client.js";
import { registerManagementTools } from "./tools/management.js";
import { registerAccountsTools } from "./tools/accounts.js";

const config: LogtoConfig = {
  endpoint: process.env.LOGTO_ENDPOINT ?? "",
  appId: process.env.LOGTO_APP_ID ?? "",
  appSecret: process.env.LOGTO_APP_SECRET ?? "",
  accountsApiToken: process.env.LOGTO_ACCOUNTS_TOKEN,
};

if (!config.endpoint || !config.appId || !config.appSecret) {
  console.error(
    "❌ Missing required environment variables.\n" +
    "   Required: LOGTO_ENDPOINT, LOGTO_APP_ID, LOGTO_APP_SECRET\n" +
    "   Optional: LOGTO_ACCOUNTS_TOKEN (enables Accounts API tools)\n\n" +
    "   Example:\n" +
    "   LOGTO_ENDPOINT=https://your-logto.example.com \\\n" +
    "   LOGTO_APP_ID=your-m2m-app-id \\\n" +
    "   LOGTO_APP_SECRET=your-m2m-app-secret \\\n" +
    "   node dist/index.js"
  );
  process.exit(1);
}

const server = new McpServer({
  name: "logto-mcp-server",
  version: "1.0.0",
  description: "Logto Management API + Accounts API for self-hosted instances",
});

// Register Management API tools (uses auto-refreshing M2M token)
registerManagementTools(server, () => getManagementClient(config));

// Register Accounts API tools (requires end-user Bearer token)
if (config.accountsApiToken) {
  registerAccountsTools(server, () => getAccountsClient(config));
  console.error("✅ Accounts API tools enabled");
} else {
  console.error("ℹ️  Accounts API tools disabled (set LOGTO_ACCOUNTS_TOKEN to enable)");
}

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`✅ Logto MCP server running — endpoint: ${config.endpoint}`);
