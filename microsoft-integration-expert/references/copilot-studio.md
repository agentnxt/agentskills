# Copilot Studio & Agent Building — Reference

Source: https://learn.microsoft.com/en-us/microsoft-copilot-studio/

## Agent Types in the Microsoft Ecosystem

### 1. Copilot Studio Agents (Low-Code)
- Built in the Copilot Studio web portal
- Natural language topic authoring + generative AI answers
- Publish to Teams, SharePoint, web, mobile, telephony
- Add actions via Power Automate, OpenAPI connectors, Graph

### 2. Declarative Agents (M365 Copilot Extension)
- Extend Microsoft 365 Copilot with custom knowledge + actions
- Defined in manifest JSON, deployed via Teams Toolkit or Admin Center
- Run inside M365 Copilot Chat
- Access Graph data, SharePoint knowledge, custom APIs
- Ref: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/

### 3. Custom Engine Agents
- Full control — bring your own LLM orchestration
- Built with: Azure AI Foundry + Semantic Kernel + Teams AI Library
- Deploy to Teams as a bot
- Best for complex reasoning, custom RAG pipelines
- Ref: https://learn.microsoft.com/en-us/azure/ai-services/

### 4. Microsoft Agent 365
- Enterprise agents embedded in Dynamics 365 and M365
- Pre-built agents: Sales Agent, Customer Service Agent, Finance Agent
- Customizable via Copilot Studio
- Ref: https://learn.microsoft.com/en-us/microsoft-agent-365/

---

## Copilot Studio: Key Concepts

### Topics
- **Trigger phrases** — Natural language phrases that start a topic
- **System topics** — Built-in (Greeting, Fallback, Error handling)
- **Generative answers** — Auto-answer from knowledge sources without topics

### Knowledge Sources
- Public websites (crawled automatically)
- SharePoint sites and OneDrive documents
- Uploaded files (PDF, Word, PowerPoint)
- Dataverse knowledge articles
- Custom data (via connectors)

### Actions (Plugins)
Connect your agent to external systems:
```
Types of actions:
├── Power Automate flows       (no-code automation)
├── OpenAPI connector actions  (REST APIs)
├── Microsoft Graph connectors
├── Prompt actions             (call Azure OpenAI directly)
└── Bot Framework skills       (advanced)
```

### Authentication Options
- **No auth** — Public-facing agents
- **Only for Teams / M365** — SSO with Entra ID (recommended)
- **Manual auth** — OAuth with any provider
- **Service auth** — App-only for actions

### Publishing Channels
- Microsoft Teams (most common)
- SharePoint web part
- Custom website (embed code)
- Power Pages
- Mobile apps (via Direct Line API)
- Azure Communication Services (voice/telephony)

---

## Declarative Agent Quick Start

### Manifest structure (declarativeAgent.json)
```json
{
  "name": "My Custom Agent",
  "description": "Helps with HR policies",
  "instructions": "You are an HR assistant...",
  "capabilities": [
    {
      "name": "WebSearch",
      "enabled": false
    },
    {
      "name": "OneDriveAndSharePoint",
      "items_by_sharepoint_ids": [
        { "site_id": "...", "list_id": "..." }
      ]
    }
  ],
  "actions": [
    {
      "id": "hrApiAction",
      "file": "hr-api-plugin.json"
    }
  ]
}
```

Deploy via Teams Toolkit: `teams toolkit provision` + `teams toolkit deploy`

---

## Semantic Kernel (Custom Engine Agents)

Semantic Kernel is Microsoft's SDK for building AI agents with plugins.

### Core concepts
- **Kernel** — The central orchestrator
- **Plugins** — Functions exposed to the LLM (native C#/Python functions or semantic prompts)
- **Planner** — Auto-selects and chains plugins to achieve a goal
- **Memory** — Vector store for RAG (Azure AI Search, Qdrant, etc.)

```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = sk.Kernel()
kernel.add_service(AzureChatCompletion(
    deployment_name="gpt-4",
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"]
))

# Add a native plugin
from semantic_kernel.functions import kernel_function

class EmailPlugin:
    @kernel_function(description="Send an email to a user")
    def send_email(self, to: str, subject: str, body: str) -> str:
        # call Graph API here
        return "Email sent"

kernel.add_plugin(EmailPlugin(), "EmailPlugin")
```

---

## Agent Design Patterns

### Pattern 1: HR / IT Helpdesk Agent
- Knowledge: SharePoint HR policies + IT docs
- Actions: Create Jira ticket (via Power Automate), look up user in Graph
- Auth: Entra ID SSO in Teams
- Channel: Teams + SharePoint web part

### Pattern 2: Sales Intelligence Agent
- Knowledge: Dynamics 365 account data + SharePoint proposals
- Actions: Update CRM opportunity, draft email via Graph/Outlook
- Auth: Entra ID + Dynamics 365 connector
- Channel: Teams + M365 Copilot (as declarative agent)

### Pattern 3: Code Review Agent (Custom Engine)
- Uses Azure OpenAI GPT-4 + GitHub API plugin
- Semantic Kernel orchestration
- Deployed as Teams bot via Azure Bot Service
- Auth: GitHub OAuth + Entra ID for Teams

---

## Responsible AI for Agents

Always configure:
1. **Content moderation** — Enable Azure AI Content Safety in Azure OpenAI
2. **Data handling notices** — Tell users what data the agent accesses
3. **Scope limiting** — Agents should only access data they need
4. **Human escalation** — Always provide a path to a human agent
5. **Audit logging** — Enable Copilot Studio analytics + Azure Monitor
6. **PII protection** — Avoid storing conversation transcripts with PII unless required
