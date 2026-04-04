# SaaS Evaluator — React Web App

AI-powered enterprise SaaS evaluation engine built on the SaaS Usability Index.

## Features

- **35 metrics** across 7 procurement stages
- **6 evaluator personas** — CISO, IT Admin, Procurement, CTO, Legal, Dept Head
- **AI auto-research** — Claude pre-populates all metrics on startup
- **Alternatives Considered** — add competitors, get side-by-side comparison table with winner detection
- **Persistent storage** — evaluations saved across sessions via `window.storage`
- **Live U-Index** — weighted score with radar chart, stage bars, blocker detection

## Usage

Drop `SaaSEvaluator.jsx` into any React project or Claude artifact environment.
Requires the Anthropic API (key injected at runtime in Claude.ai artifacts).

## Stack

- React 18 (hooks only, no external UI libraries)
- Anthropic Claude API (`claude-sonnet-4-20250514`)
- `window.storage` for persistence (Claude artifact storage API)

## Skill

The companion `SKILL.md` in the parent directory configures Claude to trigger
this evaluator via conversation.
