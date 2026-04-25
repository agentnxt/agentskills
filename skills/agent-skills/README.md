# AgentNXXT Skills

Modular agent skills and tools for multi-agent frameworks. Drop-in capabilities for CrewAI, Langflow, AutoGPT, and other agent orchestration platforms.

## Structure

```
skills/
├── crewai/          # CrewAI agent tools & skills
├── langflow/        # Langflow custom components
├── autogpt/         # AutoGPT plugins & abilities
├── composio/        # Composio tool integrations
└── shared/          # Framework-agnostic utilities
```

## Quick Start

### CrewAI
```python
from skills.crewai.web_research import WebResearchTool

agent = Agent(
    role="Researcher",
    tools=[WebResearchTool()]
)
```

### Langflow
Import custom components from `skills/langflow/` into your Langflow instance.

## Skill Categories

| Category | Description | Frameworks |
|----------|-------------|------------|
| **Research** | Web search, scraping, summarization | CrewAI, AutoGPT |
| **Data** | Database queries, ETL, analysis | CrewAI, Langflow |
| **Code** | Code generation, review, testing | CrewAI, AutoGPT |
| **Communication** | Email, Slack, notifications | All |
| **Integration** | API connectors, webhooks | Composio, All |
| **Memory** | Vector stores, knowledge bases | CrewAI, Langflow |

## Contributing

1. Create a new folder under the appropriate framework directory
2. Include a `README.md` with usage instructions
3. Add tests in a `tests/` subfolder
4. Submit a PR

## License

Apache 2.0
