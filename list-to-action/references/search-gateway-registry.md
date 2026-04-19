# Gateway Registry

The gateway registry is the extensibility layer of the list-to-action skill.
It defines which gateways the user has configured, their priority order,
and routing rules for each action type.

This mirrors how a reverse proxy or API gateway works:
- **Search actions** → routed through Search Gateways
- **Publish actions** → routed through Publish Gateways  
- **Email actions** → routed through Email Gateways
- **[future]** → extensible with new gateway types

---

## Gateway Types

```
┌─────────────────────────────────────────────────────────┐
│                    LIST ITEM + ACTION                    │
└────────────────────┬───────────────┬────────────────────┘
                     │               │
          ┌──────────▼──┐      ┌─────▼──────────┐
          │   SEARCH    │      │    PUBLISH     │
          │  GATEWAYS   │      │   GATEWAYS     │
          └──────────┬──┘      └─────┬──────────┘
                     │               │
        ┌────────────▼───┐    ┌──────▼──────────┐
        │  SearXNG (v1)  │    │  Postiz (v1)    │
        │  Brave Search  │    │  Buffer         │
        │  Tavily        │    │  Hootsuite      │
        │  Exa           │    │  Zapier webhook │
        │  Perplexity    │    │  Make.com       │
        │  Google PSE    │    │  n8n webhook    │
        │  Bing API      │    └─────────────────┘
        └────────────────┘
```

---

## User Gateway Config

Users declare their gateways in a config block (stored in the list backend
as a metadata record, or provided inline at the start of a session).

### Minimal config (SearXNG only)
```json
{
  "gateways": {
    "search": [
      {
        "id": "searxng-primary",
        "type": "searxng",
        "baseUrl": "https://searx.example.com",
        "priority": 1,
        "enabled": true
      }
    ],
    "publish": [
      {
        "id": "postiz-primary",
        "type": "postiz",
        "baseUrl": "https://api.postiz.com/public/v1",
        "apiKey": "$POSTIZ_API_KEY",
        "priority": 1,
        "enabled": true
      }
    ]
  }
}
```

### Full multi-gateway config
```json
{
  "gateways": {
    "search": [
      {
        "id": "searxng-primary",
        "type": "searxng",
        "baseUrl": "https://searx.example.com",
        "priority": 1,
        "enabled": true,
        "capabilities": ["general", "news", "science", "it", "social media", "images"]
      },
      {
        "id": "tavily-fallback",
        "type": "tavily",
        "apiKey": "$TAVILY_API_KEY",
        "priority": 2,
        "enabled": true,
        "capabilities": ["general", "news"]
      },
      {
        "id": "exa-academic",
        "type": "exa",
        "apiKey": "$EXA_API_KEY",
        "priority": 3,
        "enabled": true,
        "capabilities": ["academic", "technical"]
      }
    ],
    "publish": [
      {
        "id": "postiz-primary",
        "type": "postiz",
        "baseUrl": "https://api.postiz.com/public/v1",
        "apiKey": "$POSTIZ_API_KEY",
        "priority": 1,
        "enabled": true
      }
    ],
    "email": [
      {
        "id": "listmonk-newsletter",
        "type": "listmonk",
        "baseUrl": "https://listmonk.example.com",
        "username": "$LISTMONK_USER",
        "password": "$LISTMONK_PASS",
        "priority": 1,
        "enabled": true
      }
    ]
  }
}
```

---

## Routing Rules

### Search Gateway Routing

```
1. Check user's search gateway config (priority order)
2. Match gateway capabilities to the research profile needed
3. Try priority 1 gateway — if fails (timeout/403), fall back to priority 2
4. If ALL gateways fail → fall back to Claude's built-in web_search tool
```

**Capability-based routing:**

| Research Profile | Preferred Gateway Type | Fallback |
|---|---|---|
| GENERAL_RESEARCH | searxng | tavily → web_search |
| ACADEMIC | searxng (science cat) OR exa | tavily → web_search |
| TECHNICAL | searxng (it cat) | exa → web_search |
| NEWS_TRENDS | searxng (news cat) | tavily (news) → web_search |
| COMMUNITY_SENTIMENT | searxng (social cat) | web_search |
| COMPETITIVE | searxng | tavily → web_search |
| PRODUCT_SHOPPING | searxng | web_search |

### Publish Gateway Routing

```
1. Check which platforms are requested
2. Check user's publish gateways for those platforms
3. Postiz supports 32 platforms — route everything there first
4. For unsupported platforms → deliver as formatted draft (no publish)
```

---

## Supported Gateway Types

### 🔍 Search Gateways

#### `searxng` (PRIMARY — v1)
- **Ref:** `references/searxng-gateway.md`
- **API:** `GET /search?q=...&format=json`
- **Auth:** None (or instance token)
- **Sources:** Up to 242 engines
- **Cost:** Free (self-hosted) / Free (public instances)
- **Best for:** Everything; especially privacy-sensitive research

#### `tavily`
- **API:** `POST https://api.tavily.com/search`
- **Auth:** API key in body `{"api_key": "..."}`
- **Sources:** Curated web crawl optimised for LLMs
- **Cost:** Paid (free tier: 1,000 searches/month)
- **Best for:** Clean LLM-optimised snippets; fallback when SearXNG unavailable
- **Payload:**
```json
{
  "api_key": "$TAVILY_API_KEY",
  "query": "search query",
  "search_depth": "advanced",
  "include_answer": true,
  "include_raw_content": false,
  "max_results": 10,
  "topic": "general | news"
}
```

#### `exa`
- **API:** `POST https://api.exa.ai/search`
- **Auth:** `x-api-key` header
- **Sources:** Neural web search, strong on academic/technical
- **Cost:** Paid (free tier available)
- **Best for:** Academic papers, technical docs, semantic search
- **Payload:**
```json
{
  "query": "search query",
  "numResults": 10,
  "type": "auto | neural | keyword",
  "useAutoprompt": true,
  "category": "research paper | company | news | tweet | github"
}
```

#### `brave`
- **API:** `GET https://api.search.brave.com/res/v1/web/search`
- **Auth:** `X-Subscription-Token` header
- **Sources:** Brave's independent web index
- **Cost:** Paid (free tier: 2,000 queries/month)
- **Best for:** Privacy-respecting general search; good news results
- **Params:** `q`, `count` (max 20), `freshness` (pd/pw/pm/py), `country`, `language`

#### `perplexity`
- **API:** `POST https://api.perplexity.ai/chat/completions`
- **Auth:** `Authorization: Bearer $PERPLEXITY_API_KEY`
- **Model:** `sonar`, `sonar-pro`, `sonar-reasoning`
- **Cost:** Paid (per token)
- **Best for:** Synthesised answers with citations; complex research questions
- **Note:** Returns a synthesised answer, not raw results — use for summary, not data mining

#### `google_pse` (Programmable Search Engine)
- **API:** `GET https://www.googleapis.com/customsearch/v1`
- **Auth:** `key` + `cx` (search engine ID) params
- **Sources:** Google (scoped to configured sites or all web)
- **Cost:** Free tier 100 queries/day; paid beyond
- **Best for:** Domain-scoped searches (e.g. "search only within our docs")

#### `bing`
- **API:** `GET https://api.bing.microsoft.com/v7.0/search`
- **Auth:** `Ocp-Apim-Subscription-Key` header
- **Cost:** Paid (free tier: 1,000 transactions/month)
- **Best for:** Fallback general web search

---

### 📤 Publish Gateways

#### `postiz` (PRIMARY — v1)
- **Ref:** `references/postiz-gateway.md`
- **Platforms:** 32 (X, LinkedIn, Instagram, Facebook, Reddit, Mastodon, Bluesky, WordPress, Medium, Dev.to, Hashnode, TikTok, YouTube, Pinterest, Discord, Slack, and more)
- **Auth:** API key in `Authorization` header
- **Cost:** Free self-hosted / Paid cloud

#### `buffer` (future)
- **API:** `POST https://api.bufferapp.com/1/updates/create.json`
- **Platforms:** Twitter, LinkedIn, Facebook, Instagram, Pinterest, TikTok
- **Auth:** OAuth token

#### `hootsuite` (future)
- **API:** `POST https://platform.hootsuite.com/v1/messages`
- **Platforms:** Twitter, LinkedIn, Facebook, Instagram, YouTube, Pinterest, TikTok
- **Auth:** OAuth 2.0

#### `zapier_webhook` (future)
- **API:** `POST <zap-webhook-url>`
- **Use:** Route to any platform via Zapier automation
- **Auth:** Webhook URL is the credential
- **Payload:** `{"platform": "...", "content": "...", "metadata": {...}}`

#### `make_webhook` (future)
- Same pattern as Zapier webhook

#### `n8n_webhook` (future)
- Same pattern; self-hostable

---

### 📧 Email Gateways

#### `listmonk` (via Postiz or direct)
- **API:** REST — `POST /api/campaigns`
- **Auth:** Basic auth (username + password)
- **Best for:** Self-hosted newsletter campaigns

#### `resend` (future)
- **API:** `POST https://api.resend.com/emails`
- **Auth:** `Authorization: Bearer $RESEND_API_KEY`
- **Best for:** Transactional emails

#### `brevo` (future)
- **API:** `POST https://api.brevo.com/v3/smtp/email`
- **Auth:** `api-key` header
- **Best for:** Marketing + transactional

---

## Adding a New Gateway (Extension Guide)

To add a new gateway to this skill:

1. **Add the gateway config** to the user's gateway config JSON (see above)
2. **Add a gateway type entry** to this registry under the appropriate section
3. **Create a reference file** `references/<gateway-name>-gateway.md` with:
   - Auth setup
   - Core API call
   - Request/response shape
   - Error handling
4. **Update routing rules** — add capability mappings or platform support
5. **Reference from SKILL.md** — add to the Reference Files list

The gateway pattern is intentionally plug-and-play. New gateways don't require
changes to the core skill logic — they just need a registry entry and a reference file.

---

## Session Initialisation

At the start of each session, Claude should:

1. Check if gateway config exists in the list backend (Notion property or JSON `_gateways` key)
2. If not, ask the user for each gateway type:
   - "Do you have a SearXNG instance? (URL or skip to use built-in search)"
   - "Do you have a Postiz API key? (key or skip to get draft-only output)"
   - "Do you have an Apprise instance? (URL or skip to disable notifications)"
   - "Any other gateways? (list or skip)"
3. Store all gateway URLs/keys in session memory
4. Verify each enabled gateway with a health check before first use:
   - SearXNG: `GET /search?q=test&format=json`
   - Postiz: `GET /integrations` (with API key)
   - Apprise: `GET /status`
5. For Apprise: if configured but no key saved yet, run the Setup Wizard from `apprise-gateway.md`

---

## Notification Gateways

Notification gateways fire push alerts at lifecycle events during list processing.
They are distinct from Email gateways (bulk/campaign email) and Publish gateways (content).

```
Lifecycle Event  -->  Apprise Gateway  -->  120+ services
(item done,          (notification)         Telegram, Slack,
 error, batch                               Discord, Pushover,
 complete, etc.)                            PagerDuty, email...
```

#### `apprise` (PRIMARY -- v1)
- **Ref:** `references/apprise-gateway.md`
- **Modes:** Stateless (URL in payload) / Stateful (key + tag routing)
- **Services:** 120+ (Telegram, Slack, Discord, email, PagerDuty, Pushover, Ntfy, Gotify, Teams, and more)
- **Auth:** None by default; optional HTTP Basic Auth via Nginx override
- **Cost:** Free (self-hosted) / Free (any instance)
- **Best for:** All lifecycle notifications in list-to-action

#### `ntfy` (lightweight alternative)
- **API:** `POST https://ntfy.sh/{topic}` (or self-hosted)
- **Auth:** Optional bearer token
- **Cost:** Free (cloud) / Free (self-hosted)
- **Payload:** Plain text body or JSON `{"title":"...","message":"...","priority":3}`
- **Best for:** Simple single-topic notifications without a full Apprise setup

#### `gotify` (self-hosted alternative)
- **API:** `POST https://your-gotify/message?token={apptoken}`
- **Auth:** App token in query param
- **Cost:** Free (self-hosted only)
- **Best for:** Minimal self-hosted push without Docker complexity

---

## Notification Routing Rules

```
1. Check if APPRISE_BASE_URL is configured in session
2. If yes --> use Apprise gateway (stateful key: "list-to-action")
3. If no Apprise --> check for NTFY_URL or GOTIFY_URL
4. If none configured --> skip notification silently, log to console only
5. Notification failures NEVER block the main action
```

### When to fire notifications

| Trigger | type | tag |
|---|---|---|
| Item starts processing | info | personal |
| Research brief saved | success | content |
| Post published via Postiz | success | content |
| Email sent | success | personal |
| WordPress draft created | success | content |
| Item errored | failure | error |
| Item skipped | warning | personal |
| Batch (all items) complete | success | all |

Always read `references/apprise-gateway.md` for the exact curl patterns.
