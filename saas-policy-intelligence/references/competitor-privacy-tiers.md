# Developer Tool Privacy Tiers — Bootstrapped Reference

**Always verify against live sources before publishing.** This file is a starting point
for competitor comparisons, not a definitive source.

## AI Coding Assistants

| Tool | Free/Individual default | Paid individual | Enterprise | Air-gapped | Last verified |
|---|---|---|---|---|---|
| GitHub Copilot | Opt-OUT (trains by default from Apr 24 2026) | Opt-OUT | Never trains (DPA) | No | Mar 2026 |
| Cursor | Trains unless Privacy Mode on | Privacy Mode available | Privacy Mode forced | No | 2025 |
| Windsurf/Codeium | May use autocomplete data | Zero-retention available | Zero-retention default | Yes (self-hosted) | 2025 |
| JetBrains AI | Opt-out (collects by default) | Explicit consent required | Admin-blocked | Local models | 2025 |
| Amazon Q Developer | Opt-out for free tier | Never trains (Pro) | Never trains | No | 2025 |
| Tabnine | Never trains, never retains | Never trains, never retains | Never trains | Yes (fully air-gapped) | 2025 |

## Key dimensions to always check

When comparing any AI tool's privacy posture, verify:

1. **Training default**: opt-in vs opt-out vs never
2. **Interaction data vs content at rest**: does the tool distinguish between prompts/outputs and stored files?
3. **Enterprise exemption**: are enterprise users categorically excluded from training?
4. **Third-party model providers**: does data go to OpenAI, Anthropic, etc. for their own training?
5. **Data retention period**: how long is interaction data kept?
6. **Deletion on opt-out**: is prior data deleted or just future collection stopped?
7. **Deployment options**: SaaS-only vs VPC vs on-premises vs air-gapped
8. **Certifications**: SOC 2 Type II, ISO 27001, FedRAMP, HIPAA BAA

## Common privacy policy patterns to flag

- **The affiliate gap**: data shared with "corporate affiliates" without naming them
- **The interaction data loophole**: "we don't train on private repos" but prompts from private repos are fair game
- **The retroactive data problem**: opting out stops future collection but doesn't delete past data
- **The personal account risk**: enterprise protections don't cover developers' personal accounts
- **The sub-processor chain**: model providers, infrastructure vendors, and analytics tools each have their own policies
