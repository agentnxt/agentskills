---
did: skill:001
version: "1.0.0"
created: "2026-04-29"
name: app-alternatives-finder
description: >
  Finds and consolidates all known alternatives to any software application from multiple authoritative sources: the app's own official website/blog (self-mentioned competitors), AlternativeTo.com, Gartner Peer Insights, G2.com, and OpenSourceAlternatives.to. For each alternative, surfaces the direct link, feature overlaps, and categories (where available from listing sites). Outputs both a structured JSON payload and a human-readable Markdown report. Always trigger this skill when a user asks: "what are alternatives to X", "competitors of X", "tools like X", "what can I use instead of X", "find me alternatives", "open source alternatives to X", "compare X with similar tools", or any phrasing where the intent is to discover substitute or competing software products. Do NOT wait for the user to name all five sources — this skill handles all sourcing automatically.
---

# App Alternatives Finder

Given a target application name, discover all known alternatives from 5 sources, then produce a JSON payload and a Markdown report.

---

## Step 0 — Clarify inputs (if not already provided)

Ask the user (only if not already stated):
1. **Target app** — the software whose alternatives they want (e.g. "Notion", "Jira", "Slack")
2. **Filter** — should results include:
   - All alternatives (paid + free + open source) — **default**
   - Open source only
   - Paid/commercial only
   - Free/freemium only

If both are already clear from context, skip asking and proceed directly to research.

---

## Step 1 — Run all 5 source searches in parallel

Use `web_search` and `web_fetch` for each source. Run all searches concurrently (do not wait for one before starting the next).

### Source A — Official Website / Blog
Search for pages where the vendor themselves mention alternatives or competitors.

```
Search queries (try in order):
  "{app_name} alternatives site:{app_official_domain}"
  "{app_name} vs [competitor] site:{app_official_domain}"
  "{app_name} comparison alternatives blog"
```

- Fetch any comparison or "vs" pages found on the official domain.
- Extract: competitor names mentioned, any feature comparison table, links to those competitor pages.
- Note: This source surfaces **self-declared** alternatives — treat with appropriate skepticism (vendor bias).
- **Common pattern**: Many apps (e.g. Notion, Figma) do NOT publish competitor lists on their own site. If no official comparison page is found after 2 search attempts, record `pages_found: []` and note "No self-comparison pages found — this is common for this vendor." Do not treat this as a failure.

### Source B — AlternativeTo.com
```
URL pattern: https://alternativeto.net/software/{app-name-slug}/
Fallback search: site:alternativeto.net "{app_name}"
```

- Fetch the page and extract:
  - All listed alternatives (name, link, likes count if visible)
  - Categories/tags shown on the page
  - Feature overlaps mentioned in descriptions
  - Platform tags (Web, Windows, Mac, Linux, iOS, Android, Open Source)

### Source C — Gartner Peer Insights
```
Search: site:gartner.com/reviews "{app_name}" alternatives OR competitors
Also try: "{app_name}" gartner peer insights alternatives
```

- Fetch results and extract:
  - Gartner category / Magic Quadrant classification for the app
  - Any "compare alternatives" or "vs" pages Gartner surfaces
  - Competing products listed in the same Gartner category
  - Direct links to each alternative's Gartner page

### Source D — G2.com (via G2 MCP)

Use the `g2-mcp` MCP server tools — **do not scrape g2.com**.

```
Step 1: search_product(name="{app_name}")  →  get product UUID
Step 2: get_product(product_id)            →  star_rating, review_count, description
Step 3: get_competitors(product_id)        →  full competitor list with ratings + categories
Step 4: get_product_ratings(product_id)   →  ease_of_use, quality_of_support, ease_of_setup
Step 5: get_product_categories(product_id) → G2 categories the app belongs to
```

Extract from the MCP responses:
- All competitors: name, slug, `g2_url`, `star_rating`, `avg_rating`, `review_count`, categories
- Target app's G2 categories (from `get_product_categories`)
- Dimension ratings for the target app (from `get_product_ratings`)
- For feature comparison signals: call `get_reviews(product_id, page_size=25)` and extract the `likes` and `dislikes` fields — these are what real users say the product does/doesn't do well

If the G2 MCP server is not connected or returns an error, fall back to:
```
web_search: site:g2.com "{app_name}" alternatives
```
and note "G2 MCP unavailable — partial data from web search only."

### Source E — OpenSourceAlternatives.to
```
URL pattern: https://www.opensourcealternative.to/alternatives/{app-name}
Fallback search: site:opensourcealternative.to "{app_name}"
```

- Fetch the page and extract:
  - All listed open-source alternatives (name, link, GitHub stars if shown)
  - Categories
  - Feature overlaps / what it replaces
  - License type if shown

---

## Step 2 — Apply user filter

After collecting all results:
- If **open source only**: keep only alternatives tagged/described as open source across any source.
- If **paid/commercial only**: exclude free-only and open-source-only tools.
- If **free/freemium only**: keep only tools with a free tier or free license.
- If **all** (default): include everything, but tag each entry with its licensing model where known.

---

## Step 3 — Deduplicate and consolidate

Many alternatives will appear across multiple sources. Merge them:

```
For each unique alternative:
  - Canonical name (resolve aliases, e.g. "MS Teams" → "Microsoft Teams")
  - Sources it appeared in (list of source labels: Official, AlternativeTo, Gartner, G2, OpenSourceAlts)
  - Links: one per source where it was found + its own official URL if discoverable
  - Categories: union of all category tags across sources
  - Feature overlaps: union of all feature overlap mentions across sources
  - Open source: yes/no/partial (if known)
  - License: e.g. MIT, Apache 2.0, Proprietary, Freemium (if known)
  - Ratings: G2 rating, AlternativeTo likes (if available)
```

Sort consolidated list by **number of sources** (most widely cited first), then by G2 rating descending as tiebreaker.

---

## Step 4 — Produce JSON output

Emit a JSON block with this structure:

```json
{
  "target_app": "string",
  "filter_applied": "all | open_source_only | paid_only | free_only",
  "generated_at": "ISO 8601 date",
  "sources_searched": ["Official Website", "AlternativeTo", "Gartner Peer Insights", "G2", "OpenSourceAlternatives"],
  "alternatives": [
    {
      "name": "string",
      "official_url": "string | null",
      "sources": ["Official", "AlternativeTo", "Gartner", "G2", "OpenSourceAlts"],
      "source_links": {
        "official_mention": "url | null",
        "alternativeto": "url | null",
        "gartner": "url | null",
        "g2": "url | null",
        "opensourcealts": "url | null"
      },
      "categories": ["string"],
      "feature_overlaps": ["string"],
      "open_source": true | false | null,
      "license": "string | null",
      "ratings": {
        "g2_star_rating": "number | null",
        "g2_avg_rating": "number | null",
        "g2_review_count": "number | null",
        "g2_ease_of_use": "number | null",
        "g2_quality_of_support": "number | null",
        "g2_ease_of_setup": "number | null",
        "alternativeto_likes": "number | null"
      },
      "notes": "string | null"
    }
  ],
  "source_metadata": {
    "official_website": {
      "pages_found": ["url"],
      "vendor_bias_note": "string"
    },
    "alternativeto": {
      "page_url": "url | null",
      "total_listed": "number | null"
    },
    "gartner": {
      "category": "string | null",
      "page_url": "url | null"
    },
    "g2": {
      "product_id": "uuid | null",
      "categories": ["string"],
      "page_url": "url | null",
      "total_competitors": "number | null",
      "target_ratings": {
        "star_rating": "number | null",
        "ease_of_use": "number | null",
        "quality_of_support": "number | null",
        "ease_of_setup": "number | null"
      },
      "data_source": "g2-mcp | web_search_fallback"
    },
    "opensourcealts": {
      "page_url": "url | null",
      "total_listed": "number | null"
    }
  }
}
```

---

## Step 5 — Produce Markdown report

After the JSON block, render a human-readable report in this structure:

---

### 🔍 Alternatives to {App Name}

**Filter applied:** {filter}
**Sources searched:** Official Website · AlternativeTo · Gartner Peer Insights · G2 · OpenSourceAlternatives
**Total unique alternatives found:** {N}

---

#### 📊 Alternatives Overview

| # | Alternative | Sources | Categories | Feature Overlaps | Open Source | Links |
|---|-------------|---------|------------|-----------------|-------------|-------|
| 1 | Name | Official, G2 | CRM, Sales | Contact mgmt, Pipeline | No | [Official](#) · [G2](#) |
...

---

#### 🏷️ By Source

**Official Website (self-mentioned)**
> ⚠️ Vendor-curated list — may reflect strategic comparisons rather than full market view.
- List each alternative mentioned, with link and context quote

**AlternativeTo.com** — [View page](#)
- Category on AlternativeTo: {category}
- List alternatives with likes count and platform tags

**Gartner Peer Insights** — [View page](#)
- Gartner category: {category}
- List alternatives with Gartner links

**G2.com** — [View page](#) *(via G2 API)*
- G2 categories: {categories}
- Target app ratings: ⭐ {star_rating}/5 · Ease of use: {ease_of_use}/10 · Support: {quality_of_support}/10 · Setup: {ease_of_setup}/10
- List competitors with G2 star rating and review count

**OpenSourceAlternatives.to** — [View page](#)
- List OSS alternatives with GitHub stars and license

---

#### 🔄 Most Widely Cited (appear in 3+ sources)

Highlight the top alternatives that appear across the most sources — these are the most broadly recognized competitors.

---

#### 💡 Notes & Caveats

- Source coverage gaps (e.g. "Gartner page not found — searched but no direct category page available")
- Any aliases resolved
- Filter applied and its effect on results

---

## Error handling

- If the **G2 MCP server** is unavailable or returns an error: fall back to `web_search` on g2.com, note "G2 MCP unavailable — partial data from web search only" in `source_metadata.g2.data_source`.
- If AlternativeTo slug doesn't match: try a search fallback before giving up.
- If the app is very niche and has sparse coverage: surface whatever was found and note low coverage explicitly.
- Gartner often blocks direct fetch — if so, use search snippets to extract what's visible and note "partial data from search snippets only."

---

## Output order

Always output in this order:
1. Brief one-line confirmation of what you're researching and the filter applied
2. JSON block (fenced with ```json)
3. Markdown report (full, as specified above)

Do not truncate either output even if the list is long.
