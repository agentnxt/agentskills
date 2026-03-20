# AgentNxxt Skills

A collection of Claude skills for SaaS research, evaluation, and landing page generation.

## Skills

### saas-standardizer
23-dimension SaaS evaluation framework covering Features, Use Cases (role-specific),
Login Methods, APIs, Data Ingestion, Integrations, Pricing (via saas-cost-analyzer),
Security & Compliance, Support & SLA, Roadmap & Vision, Competitive Positioning,
Analyst Rankings (G2/Gartner), Open Source Health (GitHub/Docker), Funding & Backing,
Notable Clients, Growth Signals, Customer References, Community Sentiment,
AI & ML Capabilities, Data Privacy & Portability, Vendor Risk & Lock-in,
Implementation & Migration, and Accessibility & Internationalization.

Key behaviours:
- Webhook submission with informed user consent gate
- Human handoff via separate webhook event
- Pricing delegated to saas-cost-analyzer skill (no self-calculation)
- Integrates user-provided research from credible sources

### landing-page-generator
Generates a production-grade landing page from any existing website URL or uploaded
file. Outputs single HTML file or React component. Follows frontend-design skill
principles for distinctive, non-generic aesthetics.

## Installation
Place any `SKILL.md` in your Claude skills directory to activate.
