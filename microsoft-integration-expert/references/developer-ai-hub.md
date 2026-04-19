# Microsoft Developer AI Hub — Reference
# Source: developer.microsoft.com/en-us/ai + developer.microsoft.com/en-us/agents
# + microsoft.com/en-us/ai/tools-practices + GitHub open source courses

---

## Overview: developer.microsoft.com/en-us/ai

Microsoft's developer-facing AI portal. Three core themes:
1. **Prompt new possibilities** — Learn to build AI apps and agents
2. **Choose AI with a higher IQ** — Build/run/deploy agents with VS, GitHub, Azure
3. **Create next-gen apps responsibly** — Security + Responsible AI tooling built-in

Key message: GitHub Copilot is now **free** and integrated into VS Code.

---

## Developer Hubs (developer.microsoft.com)

| Hub | Focus | URL |
|---|---|---|
| **AI** | Build AI apps and agents | developer.microsoft.com/en-us/ai |
| **Agents** | Build agents your way (all skill levels) | developer.microsoft.com/en-us/agents |
| **Build APIs** | API-first development | developer.microsoft.com/en-us/build-apis |
| **Developer Experience** | Tooling, DX, productivity | developer.microsoft.com/en-us/developer-experience |
| **Game Development** | Xbox + game dev resources | developer.microsoft.com/en-us/games |

---

## Open Source Developer Courses (GitHub — free, self-paced)

Microsoft Cloud Advocates publish production-quality free courses on GitHub. All have code samples in Python and TypeScript.

### 1. Generative AI for Beginners — 21 Lessons
**GitHub:** https://github.com/microsoft/generative-ai-for-beginners
**Stars:** 108k+ | **Forks:** 57k+

Full lesson map:
| # | Type | Topic |
|---|---|---|
| 00 | Setup | Course setup and dev environment |
| 01 | Learn | Introduction to Generative AI and LLMs |
| 02 | Learn | Exploring and comparing different LLMs |
| 03 | Learn | Using Generative AI responsibly |
| 04 | Learn | Prompt Engineering Fundamentals |
| 05 | Build | Advanced Prompts |
| 06 | Build | Text Generation Applications |
| 07 | Build | Building Chat Applications |
| 08 | Build | Building Search Applications (Embeddings) |
| 09 | Build | Building Image Generation Applications |
| 10 | Learn | Building Low Code AI Applications |
| 11 | Build | Integrating External Applications with Function Calling |
| 12 | Build | Designing UX for AI Applications |
| 13 | Learn | Securing Your Generative AI Applications |
| 14 | Learn | The Generative AI Application Lifecycle |
| 15 | Build | RAG and Vector Databases |
| 16 | Build | Open Source Models and Hugging Face |
| 17 | Build | AI Agents |
| 18 | Build | Fine-Tuning LLMs |
| 19 | Learn | Multimodal AI |
| 20 | Learn | AI Safety and Reliability |
| 21 | Learn | Evaluation Frameworks |

Code samples in Python and TypeScript. Runs in GitHub Codespaces. Uses Azure OpenAI + GitHub Models.

### 2. AI Agents for Beginners — 12 Lessons
**GitHub:** https://github.com/microsoft/ai-agents-for-beginners
**Stars:** 50.5k+ | **Forks:** 17.7k+
**Code:** Uses Microsoft Agent Framework + Azure AI Foundry Agent Service V2

Full lesson map:
| # | Topic |
|---|---|
| 00 | Course Setup |
| 01 | Introduction to AI Agents |
| 02 | Explore Agentic Frameworks (Semantic Kernel, AutoGen, Agent Framework) |
| 03 | Agentic Design Patterns |
| 04 | Tool Use (Function calling, plugins) |
| 05 | Agentic RAG |
| 06 | Building Trustworthy Agents |
| 07 | Planning Design |
| 08 | Multi-Agent Systems |
| 09 | Metacognition in Agents |
| 10 | (additional lessons) |
| 11 | (additional lessons) |
| 12 | (additional lessons) |

Prerequisite: Generative AI for Beginners (21-lesson course above).

### 3. GitHub Copilot for Paired Programming — 9 Lessons
**Repo:** aka.ms/devcom/gh-copilot-paired-programming
Covers: Using GitHub Copilot as an AI pair programmer in VS Code, writing better code, debugging, refactoring, and AI-assisted code reviews.

### 4. AI for Beginners — 12 Weeks, 24 Lessons
**GitHub:** https://github.com/microsoft/AI-For-Beginners
Covers: Symbolic AI, Neural Networks, Deep Learning, Computer Vision (TensorFlow + PyTorch), NLP, Conversational AI, Multi-Agent Systems, Genetic Algorithms.

Community: Microsoft Foundry Discord → aka.ms/ai/discord

---

## Agents Hub — developer.microsoft.com/en-us/agents

### The AI App & Agent Factory: Microsoft Foundry

Microsoft Foundry is the unified platform for building AI apps and agents at scale.
URL: https://azure.microsoft.com/en-us/products/ai-foundry/
Docs: https://learn.microsoft.com/azure/ai-studio/

Key capabilities:
- 11,000+ foundation, open, task, and industry-specific models in model catalog
- Auto model upgrade to optimize costs
- Change models without coding
- Built into GitHub, Visual Studio, and Copilot Studio

### Tools for Building Agents (by skill level)

| Tool | Audience | Description |
|---|---|---|
| **Microsoft Copilot Studio** | Low-code / No-code | Visual canvas, pre-built tools, extend M365 Copilot, publish to Teams/web/mobile |
| **AI Toolkit for VS Code** | Developer | Create, test, deploy agents without leaving VS Code; uses GitHub Models + Foundry extensions |
| **Microsoft Foundry SDK** | Developer | Integrated SDK + APIs for full AI development lifecycle |
| **Microsoft 365 Copilot APIs** | Developer | Build intelligent GenAI experiences on M365 data (search, retrieval, chat, compliance) |
| **M365 Agents Toolkit** | Developer | VS extension for enterprise-grade custom agents across M365 Copilot, Teams, Web, 3rd-party channels |
| **M365 Agents SDK** | Pro-code Developer | Unified SDK for custom agents across M365 Copilot and additional channels |

### Getting Started with Agents
- Copilot Studio quickstart: aka.ms/agentdev/mcsgetstarted
- Copilot Studio docs: aka.ms/agentdev/mcsdocs
- AI Toolkit for VS Code: aka.ms/AIToolsPack
- AI Toolkit docs: aka.ms/AITK/docs
- Foundry SDK download: aka.ms/agentdev/foundrysdk
- M365 Copilot APIs: aka.ms/M365CopilotAPIs
- M365 Agents Toolkit: aka.ms/M365AgentsToolkit
- M365 Agents SDK: aka.ms/agents
- Model catalog: aka.ms/agentdev/modelcatalog
- Build sessions: aka.ms/agentdev/buildsessions
- Learning hub: aka.ms/agentdev/learninghub

### Community
- Discord: aka.ms/ai/discord (Microsoft Foundry Discord)
- Copilot Studio forum: aka.ms/agentdev/mcsforum
- Azure AI Foundry Developer Forum: GitHub Discussions on microsoft/azure-ai-foundry

### Customer Stories (from Agents Hub)
- **Audi AG** — Built secure, scalable AI assistant in 2 weeks using Foundry + Azure OpenAI + Azure App Service + Cosmos DB
- **Fujitsu** — Speeds time-to-market, expands security using Microsoft Dev Box + GitHub Copilot + Entra ID

---

## Responsible AI — Tools & Practices

Source: microsoft.com/en-us/ai/tools-practices
Full framework: Map → Measure → Manage

### Map Phase (Understand risks)
| Tool | Purpose |
|---|---|
| **Microsoft Responsible AI Standard** | Internal Microsoft guidance on designing, building, testing AI |
| **AI Impact Assessment Guide** | Framework for assessing AI impact before deployment |
| **AI Impact Assessment Template** | Fill-in template for structured risk assessment |
| **Human-AI Experience (HAX) Toolkit** | Design human-centered AI systems |
| **Failure Modes in Machine Learning** | Identify threats, attacks, vulnerabilities + countermeasures |
| **Inclusive Design** | Microsoft's methodology for diverse, accessible AI systems |

### Measure Phase (Evaluate)
| Tool | Purpose |
|---|---|
| **Responsible AI Dashboard** | Assess + improve model fairness, accuracy, explainability |
| **Fairlearn** | Open-source Python package — assess fairness + mitigate bias |
| **AI Red Teaming guidance** | Best practices from Microsoft AI Red Team |
| **PyRIT** | Open automation framework for red-teaming generative AI systems |
| **Threat Modeling framework** | Integrate threat modeling into your SDLC |

### Manage Phase (Operate)
| Tool | Purpose |
|---|---|
| **Microsoft Foundry Control Plane** | Centralize oversight — monitor, govern, optimize AI performance/cost/compliance |
| **Content Safety in Foundry Control Plane** | Auto-identify and block unsafe content in GenAI prompts and outputs |
| **Azure AI Content Safety** | Full service for text + image moderation |
| **Microsoft Purview** | Safeguard + manage compliance of data for AI tools/systems |

### Responsible AI Principles (6 core)
1. **Fairness** — AI must treat all people fairly
2. **Reliability & Safety** — AI must perform reliably and safely
3. **Privacy & Security** — AI must be secure and respect privacy
4. **Inclusiveness** — AI must empower everyone, including people with disabilities
5. **Transparency** — AI systems must be understandable
6. **Accountability** — People must be accountable for AI systems

URL: microsoft.com/en-us/ai/responsible-ai
Principles deep dive: microsoft.com/en-us/ai/principles-and-approach

---

## Developer Product Navigation (developer.microsoft.com)

### Products with Dev Portals
| Product | Dev Portal URL |
|---|---|
| Microsoft 365 | developer.microsoft.com/en-us/microsoft-365 |
| Microsoft Azure | developer.microsoft.com/en-us/azure |
| Microsoft Graph | developer.microsoft.com/en-us/graph |
| Microsoft Identity Platform | developer.microsoft.com/en-us/identity |
| Microsoft Teams | developer.microsoft.com/en-us/microsoft-teams |
| Microsoft Viva | developer.microsoft.com/en-us/viva |
| Power Platform | developer.microsoft.com/en-us/power-platform |
| Windows | developer.microsoft.com/en-us/windows |

### Languages Supported
.NET, C++, Java, JavaScript, Python, TypeScript

---

## Microsoft AI Product Map (from microsoft.com/en-us/ai)

### For Organizations
- Microsoft 365 Copilot — AI at work
- AI Agents at Work (M365 Copilot Agents)
- Agent 365 — Enterprise agent management
- Security for AI — Protect AI systems

### Build Your Own
- Copilot Studio — Low-code agent builder
- Microsoft Foundry — Pro-code AI app + agent platform
- Microsoft Agent Factory — Enterprise agent factory
- Azure AI apps and agents

### Industry AI Solutions
| Industry | Focus |
|---|---|
| Healthcare & Life Sciences | Providers, Payors, Life Sciences |
| Financial Services | Banking, Capital Markets, Insurance |
| Manufacturing | Industrial Transformation |
| Government | Defense, Federal, State/Local, FedRAMP |
| Retail | Consumer Goods |
| Energy & Resources | Power/Utilities, Oil/Gas, Mining |
| Mobility | Automotive, Travel/Transportation |
| Telecommunications | — |
| Media & Entertainment | — |

### For Personal Use
- Microsoft Copilot (consumer) — microsoft.com/en-us/microsoft-copilot/for-individuals
- Copilot+ PCs — AI-accelerated Windows PCs

---

## MSFT-X Developer AI Quick Reference

When a developer asks about getting started with Microsoft AI:

```
Level 0 — Never built AI:
  → Generative AI for Beginners (21-lesson GitHub course, free)
  → AI-900 for foundational cert

Level 1 — Building first AI app:
  → Azure AI Foundry quickstart
  → AI Toolkit for VS Code
  → GitHub Copilot (free in VS Code)

Level 2 — Building agents:
  → AI Agents for Beginners (12-lesson GitHub course)
  → Copilot Studio (low-code) OR M365 Agents SDK (pro-code)
  → Applied Skills: Create agents in Copilot Studio

Level 3 — Enterprise agents at scale:
  → Microsoft Foundry SDK
  → Semantic Kernel + Azure OpenAI
  → M365 Agents Toolkit for Teams deployment
  → Applied Skills: Enhance agents with autonomous capabilities

Level 4 — Responsible AI & governance:
  → AI Impact Assessment Guide + Template
  → Content Safety in Foundry Control Plane
  → PyRIT for red-teaming
  → Responsible AI Dashboard
  → Microsoft Purview for compliance
```
