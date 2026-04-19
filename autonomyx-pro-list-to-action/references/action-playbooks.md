# Action Playbooks

Detailed execution instructions for each of the three action families.

---

# Action A: Research & Summarize

## Goal
Produce a structured research brief on the item -- facts, context, trends, competitors, and
key insights -- ready to inform content creation or decision-making.

## Architecture
```
Item metadata  -->  Search Gateway  -->  Results  -->  Synthesised Brief
                   (SearXNG primary)
                   (fallback: Tavily --> Exa --> web_search built-in)
```

Read `references/searxng-gateway.md` FIRST before searching.
Read `references/search-gateway-registry.md` to understand gateway routing and fallbacks.

## Steps

### 1. Check gateway config
- Look for `SEARXNG_BASE_URL` in session or user config
- If not set, ask: "Do you have a SearXNG instance URL? (or I'll use built-in search)"
- Quick health check:
  ```bash
  curl -s "$SEARXNG_BASE_URL/search?q=test&format=json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK:', len(d.get('results',[])), 'results')"
  ```
- If 403 --> JSON disabled on instance. Try another from searx.space or fall back to `web_search`
- If SearXNG unavailable --> check gateway registry for next configured gateway --> fall back to `web_search`

### 2. Select research profile
Based on item's schema.org type (full profiles in `searxng-gateway.md` section "Research Profiles"):

| Item Type | Profile |
|---|---|
| Product / Service / SoftwareApp | GENERAL_RESEARCH + COMPETITIVE |
| Article / Blog topic | GENERAL_RESEARCH + NEWS_TRENDS |
| Person / Organization | GENERAL_RESEARCH + COMMUNITY_SENTIMENT |
| Event | NEWS_TRENDS |
| Place | LOCAL_PLACE |
| Course / Book | ACADEMIC |
| Offer / Deal | PRODUCT_SHOPPING |

### 3. Run 3-5 SearXNG queries via bash_tool

```bash
# 1. Overview
curl -s -G "$SEARXNG_BASE_URL/search" \
  --data-urlencode "q=<item_name>" \
  -d "format=json&categories=general&time_range=year" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
for r in d['results'][:5]:
    print(r['title'],'|',r['url'],'|',r.get('content','')[:200])
if d.get('infoboxes'):
    print('INFOBOX:', d['infoboxes'][0].get('content','')[:500])
"
```

Run these query variations sequentially:
1. `<item_name>` -- overview (categories=general, time_range=year)
2. `<item_name>` -- news (categories=news, time_range=month)
3. `<item_name> review` -- community sentiment (engines=reddit,hackernews)
4. `<item_name> vs alternatives` -- competitive (categories=general)
5. Type-specific: categories=science (academic) OR categories=it (technical)

### 4. Fetch full content for top 2-3 results
Use `web_fetch` on high-score, multi-engine results and any infoboxes sources.
Prioritise: infobox sources > official item URL > multi-engine results.

### 5. Synthesise Research Brief
Use the brief template from `searxng-gateway.md` section "Synthesising the Research Brief":
- Summary, Key Facts, Trends, Audience/Sentiment, Competitive Landscape, Content Angles, Sources

### 6. Save and update item
- Save as `<item-name>-research.md`, present via `present_files`
- Update item `notes` in backend, status --> done, actionTaken --> research

---

# Action B: Write & Publish

## Goal
Generate platform-optimized content for the item, then publish to ALL selected platforms
via the **Postiz Publishing Gateway** -- a single API call that reaches 32 channels at once.

## Architecture
```
Claude writes content  -->  Postiz API  -->  32 platforms simultaneously
(per-platform format)       (gateway)        (X, LinkedIn, Instagram, Reddit, etc.)
```

Read `references/postiz-gateway.md` FIRST before publishing. It contains:
- Authentication setup
- How to discover connected channels (integration IDs)
- How to upload media
- Platform-specific settings schemas
- The unified POST payload structure

## Publishing Flow

1. Ask user which platforms to publish to (or use defaults from item metadata platform[])
2. Generate content for each platform (see platform content rules below)
3. Check Postiz integrations -- confirm the user has those channels connected
4. Upload media if the item has an image (Step 1 in postiz-gateway.md)
5. Build unified payload -- all platforms in one posts[] array
6. Show the full payload to the user -- ask for confirmation before sending
7. POST to Postiz in a single request
8. Report results per platform (QUEUE / PUBLISHED / ERROR)
9. Update item status --> done

## Platform Playbooks

Ask the user which platform(s) to write for. Default: write for all selected platforms.

---

### LinkedIn Post
**Postiz __type:** `linkedin` or `linkedin-page` | **Publishes via:** Postiz gateway

**Constraints:** 1,300 characters max for best reach (3,000 API max). 3-5 hashtags.

**Structure:**
```
[Hook line -- bold claim, question, or counterintuitive statement]

[2-3 short paragraphs -- story, insight, or value]

[1-2 lines -- key takeaway]

[CTA -- question to drive comments, or "Link in comments"]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Tone:** Professional but human. First person. No corporate jargon. Short sentences.

---

### Twitter / X Thread
**Postiz __type:** `x` | **Publishes via:** Postiz gateway

**Constraints:** Each tweet <=280 characters. Threads = multiple objects in the value array.

**Structure:**
```
Tweet 1 (Hook): Bold claim or question. "Thread:"
Tweet 2-N: One idea per tweet. Use numbers (2/, 3/) or emojis as bullets.
Last tweet: CTA -- follow, retweet, reply, or link.
```

**Tone:** Punchy. Direct. Opinionated. No fluff. Each tweet must stand alone.

---

### Instagram Caption
**Postiz __type:** `instagram` or `instagram-standalone` | post_type: post|reel|story | **Publishes via:** Postiz gateway

**Constraints:** 2,200 characters max. First 125 chars must hook before "more". 20-30 hashtags.

**Structure:**
```
[Hook -- first 1-2 lines, must compel tap "more"]

[Body -- story, value, or how-to in short paragraphs]

[CTA -- "Save this post", "Tag someone", "Link in bio"]

#hashtag1 #hashtag2 ... (20-30 hashtags)
```

**Tone:** Visual storytelling. Warm, aspirational, or educational.
**Note:** Always suggest an image description / visual prompt for the post.

---

### Meta / Facebook Post
**Postiz __type:** `facebook` | **Publishes via:** Postiz gateway

**Constraints:** 200-500 words for best reach. Links can go in body.

**Structure:**
```
[Hook -- 1-2 lines]
[Body -- 2-4 paragraphs]
[CTA -- question or link]
```

**Tone:** Conversational. Community-oriented. Slightly longer and more personal than LinkedIn.

---

### Reddit Post
**Postiz __type:** `reddit` | Requires: subreddit[] with title per subreddit | **Publishes via:** Postiz gateway

**Constraints:** Title <=300 characters. Body: Markdown. Always suggest 2-3 relevant subreddits.

**Structure:**
```
Title: [Specific, value-forward, no clickbait]

Body:
[Context paragraph]
[Main value / insight / question]
[Optional: bullet points for listicles]
[CTA -- "What do you think?"]
```

**Tone:** Humble. Community-first. Transparent. Avoid overt self-promotion.

---

### Mastodon Post
**Postiz __type:** `mastodon` | **Publishes via:** Postiz gateway

**Constraints:** 500 characters. Hashtags drive discovery.

```
[1-3 sentences of value or insight]
[CTA if space allows]
#Hashtag1 #Hashtag2 #Hashtag3
```

**Tone:** Open web ethos. Thoughtful. Community-oriented.

---

### Bluesky Post
**Postiz __type:** `bluesky` | **Publishes via:** Postiz gateway

**Constraints:** 300 characters per post. Threads supported.

```
[Punchy insight or hook]
[1-2 lines of value]
[CTA or hashtag]
```

**Tone:** Early-adopter, thoughtful, internet-native.

---

### Beehiiv Newsletter Section
**Postiz:** Beehiiv is not a direct Postiz channel. Route to Listmonk via Postiz (__type: "listmonk") OR deliver as Markdown draft for manual paste.

**Structure:**
```markdown
## [Section Title]
[1-2 sentence intro / hook]
[Body -- 2-4 paragraphs or a structured list]
[CTA -- link, subscribe nudge, or discussion prompt]
---
```

**Tone:** Curated. Smart. Written for the reader, not broadcast at them.
**Output:** Deliver as Markdown. Suggest subject line if this will be a full issue.

---

### WordPress Blog Post
**Postiz __type:** `wordpress` | Settings: title, main_image, type: "post" | **Publishes via:** Postiz gateway

Always create as `draft` -- user reviews and publishes from WordPress dashboard.

**Constraints:** Full long-form. SEO-optimized. 800-2,500 words typical.

**Structure:**
```markdown
# [SEO Title -- include primary keyword]

**[Meta description -- 150-160 chars for SEO]**

## Introduction
[Hook + problem statement + what reader will learn]

## [Section 1]
[Body content]

## Conclusion
[Summary + CTA]

---
Tags: keyword1, keyword2
Category: [suggested]
```

After user confirms, build the Postiz payload with __type: "wordpress" and POST.
See `references/postiz-gateway.md` for the full settings schema.

---

### Long-form Blog (Markdown File)

Same structure as WordPress post. Save as `<item-name>-blog.md` and present via `present_files`.
User can paste into any CMS, or re-trigger a Postiz publish to Medium, Hashnode, or Dev.to.

---

## Post-Write Checklist (run for every platform)

- Hook is strong -- would you stop scrolling?
- CTA is clear and specific
- No filler words ("very", "really", "just", "actually")
- Length is within platform constraints
- Hashtags are relevant (not stuffed)
- Tone matches the platform

---

# Action C: Draft & Send Email

## Goal
Compose a targeted email based on the item's metadata, present it to the user for confirmation, then send.

## Steps

### 1. Gather email parameters
Ask if not in item metadata:
- To: recipient email(s)
- Subject: (Claude suggests, user can edit)
- Purpose: announcement, outreach, newsletter, follow-up, pitch, etc.
- Tone: formal / conversational / warm / urgent

### 2. Draft the email

**Structure:**
```
Subject: [Specific, benefit-forward, <=60 chars]

Hi [Name / Team],

[Opening line -- reason for writing, no "Hope this finds you well"]

[Para 1: Context / what this is about]
[Para 2: The value / why it matters to them]
[Para 3: What you're asking or offering]

[CTA -- one clear ask: reply, click, schedule, review]

[Sign-off],
[Sender name]
```

**Tone rules:** No passive voice. Max 3 sentences per paragraph. One CTA only.

### 3. Present draft to user
Display full email. Ask: "Does this look good? Reply 'send' to send, or tell me what to change."

### 4. Send (after explicit confirmation)
Use message_compose_v1 tool or available email MCP.
If no email tool connected: present as file, user copies and sends manually.

### 5. Log
Update item: status --> done, actionTaken --> email_sent, outputRef --> email:<subject>:<timestamp>

---

## Choosing the Right Action

If the user hasn't specified an action, suggest based on item type:

| Item Type | Suggested Action |
|---|---|
| Product / Service / SoftwareApplication | Write (LinkedIn + Blog) |
| Article / BlogPosting | Write (Long-form Blog + WordPress) |
| Person / Organization | Research first, then Write (LinkedIn) |
| Event | Write (LinkedIn + Email announcement) |
| Place / ImageObject | Write (Instagram + Blog) |
| Recipe | Write (Instagram + Blog) |
| JobPosting | Write (LinkedIn + Email outreach) |
| Offer / Deal | Write (all social platforms + Email) |
| Course / Book | Research + Write (LinkedIn + Beehiiv) |
| Generic Topic | Research first, then Write |
