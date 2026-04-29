---
did: skill:008
version: "1.0.0"
created: "2026-04-29"
featureFlag: "beta"
name: autonomyx-pro-list-to-action
description: >
  Autonomyx.Pro — Queue-driven content and research automation for SaaS teams.
  Processes a persistent list of items (products, services, topics, people, events, images, etc.)
  and performs an action on the next pending item. Supports web research, writing for 10+ platforms
  (LinkedIn, Twitter/X, Instagram, Facebook, Reddit, Mastodon, Bluesky, Beehiiv, WordPress,
  Markdown blog), and draft-then-send email. List can live in Notion, JSON file, or be pasted inline.
  Trigger on: "process my list", "next item in my queue", "write a post for the next product",
  "research the next topic", "run my content queue", "work through my list", or any phrase combining
  "list" / "queue" / "next item" / "batch" with a content, research, or email action.
  Also trigger when user pastes a list and says what to do with it. Do NOT wait for explicit skill name.
---

# Autonomyx.Pro — List-to-Action

> **Autonomyx.Pro** is the queue-driven automation layer of the Autonomyx SaaS platform.
> It picks the next **pending** item from a persistent list, identifies its schema.org type,
> enriches its metadata if needed, and executes one of three action families:
> **Research**, **Write/Publish**, or **Email**.

---

## Step 0 — Identify the List Source

Ask the user (or infer from context) where their list lives:

| Backend | How to Read | How to Write Status |
|---|---|---|
| **Notion DB** | Use `notion-search` or `notion-fetch` with the DB URL | Use `notion-update-page` to set status field |
| **JSON file** | Read with `bash_tool` (`cat <path>`) | Overwrite file with updated status |
| **Pasted inline** | User provides the list directly in chat | Maintain state in conversation; remind user to save |

Read the `references/backends.md` file for exact tool call patterns for each backend.

If the source is unknown, ask: *"Where is your list stored? (Notion, JSON file, or paste it here)"*

---

## Step 1 — Pick the Next Pending Item

- Filter items where `status` = `pending` (or equivalent: `todo`, `not started`, `queued`, `""`)
- Pick the **first** matching item in order (top of list = highest priority)
- If no pending items exist, tell the user: *"✅ Autonomyx.Pro: Queue complete — no pending items found."*
- Display the selected item to the user before proceeding:

```
🤖 Autonomyx.Pro — Next Item
📋 Item:   [name]
🏷  Type:   [schema.org type]
⚙️  Status: pending → in_progress
```

Update the item's status to `in_progress` immediately.

---

## Step 2 — Identify the Item's Schema.org Type

Use the item's fields and context to classify it. Read `references/schema-types.md` for the full type map and required/optional metadata fields for each type.

Core types supported:
- `Product` · `Service` · `SoftwareApplication`
- `CreativeWork` · `Article` · `BlogPosting`
- `Person` · `Organization`
- `Event` · `Place`
- `ImageObject` · `VideoObject`
- `Recipe` · `Course` · `Book`
- `JobPosting` · `Offer`
- `SocialMediaPosting` · `EmailMessage`

If type is ambiguous, make a best-guess and state it. Do not ask unless genuinely impossible to infer.

---

## Step 3 — Enrich Metadata (if fields are missing)

If the item is missing key metadata fields for its type (e.g., a Product has no description):

1. Check if the item has a `url` or `sameAs` field — use `web_search` + `web_fetch` to pull missing data
2. Fill in: `description`, `keywords`, `targetAudience`, `category`, `image` (prompt) as applicable
3. Show the enriched metadata to the user before acting

---

## Step 4 — Execute the Action

Ask the user which action to perform (or infer from context / a default set in their list):

### 🔍 Action A: Research & Summarize via SearXNG
→ Read `references/action-playbooks.md` § Research, then `references/searxng-gateway.md`
All research routes through the SearXNG Search Gateway (242 engines, category-based, privacy-first).
Fallback chain: SearXNG → Tavily → Exa → built-in web_search.
See `references/search-gateway-registry.md` for adding other search gateways.

### ✍️ Action B: Write & Publish via Postiz
→ Read `references/action-playbooks.md` § Write-Publish, then `references/postiz-gateway.md`
All publishing routes through the Postiz API — one request, up to 32 platforms simultaneously.
Platforms: X · LinkedIn · Instagram · Facebook · Reddit · Mastodon · Bluesky · Threads · TikTok · YouTube · Pinterest · Discord · Slack · Medium · Dev.to · Hashnode · WordPress · Google My Business · Listmonk · and more.

### 🔔 Action D: Notify via Apprise (runs automatically at lifecycle events)
→ Read `references/apprise-gateway.md`
Fires push notifications at key events: item start, action complete, publish success, error, batch done.
Supports 120+ services (Telegram, Slack, Discord, Pushover, email, PagerDuty, Ntfy, Gotify, Teams...).
Uses stateful key `autonomyx-pro` with tag-based routing (personal / content / ops / error / all).
**Notification failures never block the main action.**

### 📧 Action C: Draft & Send Email
→ Read `references/action-playbooks.md` § Email

---

## Step 5 — Mark Item Complete & Notify

After the action is successfully executed (or output delivered to user):

- Update item status: `in_progress` → `done`
- Set `completedAt` = current date/time (ISO 8601)
- Set `actionTaken` = action label (e.g., `"linkedin_post"`, `"research"`, `"email_draft"`)
- If the action produced a URL or file, store in `outputUrl` or `outputRef`
- Prefix all completion messages with `🤖 Autonomyx.Pro:`

**Fire Apprise notification** (if configured):
→ Read `references/apprise-gateway.md` § Notification Triggers
→ type: `success`, tag: appropriate (content/personal/ops), body: summary of what was done

Ask: *"🤖 Autonomyx.Pro: Ready to process the next item?"*

---

## Error Handling

| Situation | Response |
|---|---|
| Item missing critical fields and no URL to enrich from | Ask user to fill the gaps before proceeding |
| Notion MCP call fails | Fall back to asking user to paste the item |
| Platform-specific length exceeded | Truncate gracefully + note what was cut |
| Email send fails | Keep status as `in_progress`, show draft, ask user to retry |
| WordPress publish fails | Save as Markdown file, present to user |

All errors are prefixed: `🤖 Autonomyx.Pro [ERROR]:`

---

## Reference Files

Read these files **only when needed** — do not pre-load all of them:

- `references/backends.md` — Tool call patterns for Notion and JSON backends
- `references/schema-types.md` — Schema.org type definitions and metadata fields
- `references/action-playbooks.md` — Orchestration for Research, Write/Publish, and Email actions
- `references/searxng-gateway.md` — **SearXNG Search Gateway** (API, 242 engines, categories, research profiles, brief template)
- `references/postiz-gateway.md` — **Postiz Publish Gateway** (auth, channels, media upload, 32-platform settings, unified payload)
- `references/apprise-gateway.md` — **Apprise Notification Gateway** (stateless + stateful modes, 120+ services, URL schemes, lifecycle triggers, file attachments)
- `references/search-gateway-registry.md` — **Gateway Registry** (all gateway types incl. notification, routing rules, fallback chains, how to add new gateways)

---

*Powered by [Autonomyx.Pro](https://autonomyx.pro) — Intelligent SaaS Automation*
