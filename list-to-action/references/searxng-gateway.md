# SearXNG Search Gateway

SearXNG is the unified search layer for all research actions.
One API call → results aggregated from up to 242 search engines simultaneously.
Privacy-first, self-hostable, open-source.

**Docs:** https://docs.searxng.org/dev/search_api.html
**Public instances:** https://searx.space (find one with JSON enabled)

---

## Setup Requirements

```
SEARXNG_BASE_URL=https://your-instance.example.com   # or public instance
# No API key required for most instances
# Some self-hosted instances may require a secret key in settings.yml
```

To verify JSON is enabled on your instance:
```bash
curl -s "$SEARXNG_BASE_URL/search?q=test&format=json" | python3 -m json.tool
```
If you get `403 Forbidden`, this instance has JSON disabled — pick another from searx.space
or self-host.

---

## Core API Call

```bash
curl -s -G "$SEARXNG_BASE_URL/search" \
  --data-urlencode "q=<query>" \
  -d "format=json" \
  -d "categories=<categories>" \
  -d "engines=<engines>" \
  -d "language=en" \
  -d "time_range=<day|month|year>" \
  -d "pageno=1"
```

### Parameters

| Parameter | Required | Values | Notes |
|---|---|---|---|
| `q` | ✅ | Any string | Supports engine-specific syntax |
| `format` | ✅ | `json`, `csv`, `rss` | Always use `json` |
| `categories` | ○ | See below | Comma-separated |
| `engines` | ○ | See below | Comma-separated; overrides categories |
| `language` | ○ | `en`, `fr`, `de`... | ISO language code |
| `pageno` | ○ | `1`, `2`, `3`... | Pagination |
| `time_range` | ○ | `day`, `month`, `year` | Recency filter |
| `safesearch` | ○ | `0`, `1`, `2` | 0=off, 1=moderate, 2=strict |

### Response shape

```json
{
  "query": "your query",
  "number_of_results": 42,
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com/page",
      "content": "Snippet text from the page...",
      "engine": "google",
      "engines": ["google", "duckduckgo"],
      "score": 1.0,
      "category": "general",
      "publishedDate": "2024-01-15T00:00:00Z"
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [
    {
      "infobox": "Entity Name",
      "content": "Wikipedia-style summary...",
      "urls": [...]
    }
  ],
  "suggestions": ["related query 1", "related query 2"]
}
```

**Key fields to use:**
- `results[].title` + `results[].url` + `results[].content` → core result
- `infoboxes[].content` → rich entity summaries (Wikipedia etc.) — use first
- `answers[]` → direct answers for factual queries
- `results[].publishedDate` → for recency sorting

---

## Categories Reference

Categories activate groups of engines. Use these as your first routing decision:

| Category | What it searches | Best for |
|---|---|---|
| `general` | Google, Bing, DuckDuckGo, Brave, Startpage... | Broad web research |
| `news` | Google News, Bing News, Reuters, AP... | Current events, recent coverage |
| `science` | Arxiv, Semantic Scholar, PubMed, CrossRef... | Academic, research papers |
| `it` | GitHub, StackOverflow, HackerNews, npm... | Technical / developer queries |
| `images` | Google Images, Bing Images, Unsplash... | Image search |
| `videos` | YouTube, Vimeo, Dailymotion... | Video content |
| `social media` | Reddit, Lemmy... | Community discussions |
| `files` | Archive.org, various file hosts... | Documents, PDFs |
| `map` | OpenStreetMap, Google Maps... | Location queries |
| `music` | SoundCloud, Bandcamp, Mixcloud... | Audio/music |
| `onions` | Ahmia, Torch... | Tor hidden services |

---

## Engine Selection (Fine-Grained Control)

Instead of or in addition to categories, specify exact engines:

### General Web
`google`, `bing`, `duckduckgo`, `brave`, `startpage`, `qwant`, `yahoo`, `ecosia`

### Academic / Science
`arxiv`, `semantic scholar`, `pubmed`, `crossref`, `google scholar`, `unpaywall`

### Developer / Technical
`github`, `gitlab`, `stackoverflow`, `npm`, `pypi`, `crates.io`, `hackernews`

### News
`google news`, `bing news`, `reuters`, `the guardian`, `ap`

### Social / Community
`reddit`, `lemmy`, `mastodon`

### Knowledge / Reference
`wikipedia`, `wikidata`, `currency`, `ddg definitions`

### Shopping / Products
`amazon`, `ebay`, `google shopping`, `bing shopping`

### Images
`google images`, `bing images`, `unsplash`, `flickr`, `deviantart`

### Videos
`youtube`, `vimeo`, `dailymotion`, `invidious`

### Maps / Places
`openstreetmap`, `google maps`, `photon`

---

## Research Profiles (Pre-built Query Strategies)

Load these based on the item's schema.org type and research goal:

### Profile: GENERAL_RESEARCH
For: Product, Service, SoftwareApplication, Organization, CreativeWork
```
categories=general,news
time_range=year
pageno=1 (then pageno=2 for more depth)
```

### Profile: ACADEMIC
For: Course, Book, scientific topics, technical research
```
categories=science,it
engines=arxiv,semantic scholar,wikipedia,pubmed
time_range=year
```

### Profile: TECHNICAL
For: SoftwareApplication, API, developer tools
```
categories=it
engines=github,stackoverflow,hackernews,npm,pypi
```

### Profile: NEWS_TRENDS
For: Event, recent developments, market trends
```
categories=news,general
time_range=month
```

### Profile: COMMUNITY_SENTIMENT
For: understanding what users think, reviews, discussions
```
categories=social media,general
engines=reddit,hackernews
```

### Profile: COMPETITIVE
For: comparing alternatives, market positioning
```
categories=general
q="{name} vs alternatives" OR "{name} competitors"
time_range=year
```

### Profile: LOCAL_PLACE
For: Place, Event (location-based)
```
categories=map,general
engines=openstreetmap,google maps,wikipedia
```

### Profile: PRODUCT_SHOPPING
For: Product pricing, availability, reviews
```
categories=general
engines=amazon,ebay,google shopping
```

---

## Multi-Query Research Strategy

For thorough research, run **3–5 queries** in sequence:

```python
queries = [
    # 1. Primary overview
    {"q": f"{item_name}", "categories": "general", "time_range": "year"},

    # 2. Recent news
    {"q": f"{item_name}", "categories": "news", "time_range": "month"},

    # 3. Type-specific deep dive (pick profile from above)
    {"q": f"{item_name} review analysis", "categories": "general,social media"},

    # 4. Competitive / comparative
    {"q": f"{item_name} vs alternatives", "categories": "general", "time_range": "year"},

    # 5. Community discussion
    {"q": f"{item_name}", "engines": "reddit,hackernews", "time_range": "year"},
]
```

Run each sequentially with `bash_tool`. Deduplicate results by URL. Rank by score.

---

## Fetching Full Page Content

SearXNG returns snippets (~200 chars). For deep research, fetch full content from top results:

```bash
# Fetch top 2-3 URLs from results
curl -s --max-time 10 -A "Mozilla/5.0" "<result_url>"
```

Or use `web_fetch` tool for cleaner extraction.

Prioritise fetching:
1. Results with `infoboxes` (Wikipedia-quality summaries)
2. Official docs / company pages (match item's `url` field)
3. High-score results from multiple engines (`engines` array length > 1)

---

## Synthesising the Research Brief

After collecting results, produce this structured output:

```markdown
## Research Brief: [Item Name]
**Schema Type:** [e.g., Product]
**Researched:** [ISO date]
**Sources:** [N results from SearXNG across N engines]

### Summary
2–3 sentence overview synthesised from top results and infoboxes.

### Key Facts
- Fact 1 (source: url)
- Fact 2 (source: url)
- ...5–8 facts max

### Trends & Recent Developments
What's happening now, based on news results (time_range: month).

### Target Audience / Community Sentiment
Who uses/discusses this and how they talk about it (Reddit/HN results).

### Competitive Landscape
Top 3–5 alternatives or comparators found in results.

### Content Angles
3–5 specific angles Claude could use for blog posts, social posts, or emails.

### Sources Consulted
- [Title](url) — engine(s)
- ...
```

Save as `<item-name>-research.md` in outputs. Update item `notes` field in backend.

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `403 Forbidden` | JSON format disabled on instance | Switch to another instance (searx.space) |
| Empty `results[]` | Query too narrow or engines offline | Broaden query, try different engines |
| Timeout | Instance overloaded | Retry or switch instance |
| Malformed JSON | Instance returning HTML error page | Check SEARXNG_BASE_URL is correct |

---

## Extending to Other Search Gateways

SearXNG is the **primary** search gateway. See `references/search-gateway-registry.md`
for how to add and route to alternative gateways (Brave Search API, Tavily, Exa, Perplexity,
Google PSE, Bing API, etc.) when SearXNG is unavailable or a specialist source is needed.
