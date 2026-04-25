# AutonomyX n8n Orchestrator

Build and manage n8n workflows on the AutonomyX platform.

## Instance Details
- **Editor UI**: https://n8n-bot.agnxxt.com (also https://api.openautonomyx.com)
- **Internal API**: http://localhost:5678 (on unboxd.cloud)
- **Version**: 2.14.2
- **Auth**: `admin@agnxxt.com` / `Admin@123`
- **Container**: `n8n-bot` (bridge network, port 5678)
- **Server**: unboxd.cloud

## n8n MCP Server
- **Container**: `mcp-n8n` (image: thefractionalpm/mcp-n8n:latest)
- **Internal**: http://172.16.1.77:3000
- **Networks**: mcphub_mcphub, platform_internal
- **Endpoints**: `/sse`, `/mcp`, `/health`
- **Transport**: SSE at `/sse`, Streamable HTTP at `/mcp`

## Other n8n Containers
- `a2a-n8n` — Agent-to-agent sidecar
- `mcp-n8n` — MCP server sidecar (tools for workflow management)

## n8n API Reference

### Authentication
Login via cookie-based auth:
```bash
curl -c cookies.txt -X POST http://localhost:5678/rest/login \
  -H 'Content-Type: application/json' \
  -d '{"emailOrLdapLoginId":"admin@agnxxt.com","password":"Admin@123"}'
```

Or create an API key in the n8n UI for header-based auth:
```
X-N8N-API-KEY: <api-key>
```

### Key Endpoints
- **List workflows**: GET `/api/v1/workflows`
- **Get workflow**: GET `/api/v1/workflows/{id}`
- **Create workflow**: POST `/api/v1/workflows`
- **Update workflow**: PUT `/api/v1/workflows/{id}`
- **Delete workflow**: DELETE `/api/v1/workflows/{id}`
- **Activate workflow**: POST `/api/v1/workflows/{id}/activate`
- **Deactivate workflow**: POST `/api/v1/workflows/{id}/deactivate`
- **Execute workflow**: POST `/api/v1/workflows/{id}/run`
- **List executions**: GET `/api/v1/executions`
- **List credentials**: GET `/api/v1/credentials`

### Workflow JSON Structure
```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "parameters": {},
      "id": "uuid",
      "name": "Node Name",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {
    "Node Name": {
      "main": [[{"node": "Next Node", "type": "main", "index": 0}]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

### Common Node Types
- `n8n-nodes-base.manualTrigger` — Manual trigger
- `n8n-nodes-base.webhook` — Webhook trigger
- `n8n-nodes-base.scheduleTrigger` — Cron/schedule trigger
- `n8n-nodes-base.httpRequest` — HTTP Request
- `n8n-nodes-base.code` — JavaScript/Python code
- `n8n-nodes-base.set` — Set values
- `n8n-nodes-base.if` — Conditional
- `n8n-nodes-base.splitInBatches` — Batch processing
- `n8n-nodes-base.merge` — Merge data
- `n8n-nodes-base.googleSheets` — Google Sheets
- `n8n-nodes-base.noOp` — No operation (pass-through)

### n8n MCP Tools (via mcp-n8n)
Access via MCP protocol at `http://172.16.1.77:3000/mcp` or SSE at `/sse`.
Use JSON-RPC 2.0 format:
```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"tool_name","arguments":{...}}}
```

## Connected Services
- **Firecrawl**: http://172.16.1.112:3002 (webcrawl-api on platform_internal)
- **Ollama**: http://localllm:11434 (qwen2.5:7b) — accessible from platform_internal
- **Liferay**: https://www.openautonomyx.com (auth: test@liferay.com / 123456)
- **Langflow**: http://172.16.2.20:7860 (on platform_frontend)

## Notes
- n8n-bot is on the `bridge` network — to connect it to other services, use `docker network connect`
- The `n8n-nodes-base.executeCommand` node type is NOT available in this n8n version (causes activation errors)
- Use `n8n-nodes-base.code` node instead for custom logic
