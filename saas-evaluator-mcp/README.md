# saas-evaluator-mcp

MCP server for the **SaaS Usability Index** — multi-persona enterprise SaaS evaluation engine.
Built by [Autonomyx](https://openautonomyx.com). Part of the [AgentSkills](https://github.com/agentnxxt/agentskills) suite.

## Tools

| Tool | Description |
|------|-------------|
| `start_evaluation` | Begin evaluation; Claude auto-researches all 35 metrics |
| `score_metric` | Set/override a score (0–5) for any metric |
| `get_evaluation_status` | U-Index, stage breakdown, persona status, blockers |
| `mark_persona_complete` | Mark a persona's section done (ciso, it-admin, procurement, cto, legal, dept-head) |
| `add_alternative` | Research a competitor for side-by-side comparison |
| `compare_alternatives` | Full metric comparison table with winner detection |
| `get_report` | Complete evaluation report with procurement recommendation |
| `list_evaluations` | List all evaluations on the server |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/agentnxxt/saas-evaluator-mcp.git
cd saas-evaluator-mcp

# 2. Run with Docker Compose
ANTHROPIC_API_KEY=sk-ant-... docker-compose up --build

# 3. Connect to Claude Desktop (add to claude_desktop_config.json):
```

```json
{
  "mcpServers": {
    "saas-evaluator": {
      "command": "docker",
      "args": ["run", "--rm", "-e", "ANTHROPIC_API_KEY", "-v", "eval_data:/data", "openautonomyx/saas-evaluator-mcp:latest"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for auto-research |
| `EVAL_DATA_DIR` | No | Path for evaluation data (default: `/tmp/saas-evaluator-data`) |

## Local Development

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-ant-... python server.py

# Run tests (no API key needed)
pytest test_server.py -v
```

## CI/CD

GitHub Actions runs tests on every push and builds + pushes a Docker image to Docker Hub on `main`.

Add these secrets to your GitHub repo:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## Scoring Model

**U-Index** = weighted average across 7 stages (0–5 scale)

| Score | Verdict |
|-------|---------|
| 4.0–5.0 | Strong — Recommended |
| 3.0–3.9 | Enterprise Baseline — Approvable with monitoring |
| 2.0–2.9 | Emerging — Conditional |
| 0–1.9 | Not Enterprise-Ready — Do Not Procure |

🚨 Any metric scoring 0–1 in Stages 2, 4, or 5 is flagged as a **procurement blocker**.

## License

Apache 2.0 — Autonomyx / OpenAutonomyx
