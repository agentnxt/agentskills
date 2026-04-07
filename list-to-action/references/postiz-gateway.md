# Postiz Publishing Gateway

Postiz is the unified publishing layer for all social media and content platforms.
Instead of calling each platform individually, Claude routes ALL publishing through
the Postiz API — one key, 32 channels.

**Docs:** https://docs.postiz.com/public-api/introduction
**Rate limit:** 30 requests/hour (batch multiple platforms in ONE request to maximise throughput)

---

## Setup Requirements

The user must have:
1. A Postiz account (cloud: postiz.com, or self-hosted)
2. An API key from **Settings > Developers > Public API**
3. Connected channels (integrations) in the Postiz dashboard

Ask the user for:
```
POSTIZ_API_KEY=<their api key>
POSTIZ_BASE_URL=https://api.postiz.com/public/v1   # or self-hosted URL
```

Store these in the session. Never log or expose the API key.

---

## Step 0: Discover Connected Channels

Before publishing, always fetch the user's live integrations to get real integration IDs:

```bash
curl -s -H "Authorization: $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/integrations" | python3 -m json.tool
```

Response shape:
```json
[
  {
    "id": "cm4ean69r0003w8w1cdomox9n",
    "name": "My LinkedIn",
    "identifier": "linkedin",
    "picture": "https://...",
    "disabled": false,
    "profile": "username"
  }
]
```

**Cache this list for the session.** Build a lookup map: `{ "linkedin": "cm4ean...", "x": "...", ... }`

If a channel the user wants to publish to is `disabled: true` or missing, inform them to connect it in Postiz first.

---

## Step 1: Upload Media (if post has images/video)

If the item has an `image` field (URL or file path), upload it first:

### Upload from URL
```bash
curl -s -X POST "$POSTIZ_BASE_URL/uploads/upload-from-url" \
  -H "Authorization: $POSTIZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

### Upload from local file
```bash
curl -s -X POST "$POSTIZ_BASE_URL/uploads/upload-file" \
  -H "Authorization: $POSTIZ_API_KEY" \
  -F "file=@/path/to/image.jpg"
```

Response:
```json
{ "id": "img-abc123", "path": "https://uploads.postiz.com/image.jpg" }
```

Store the `id` and `path` — use them in the posts payload under `"image"`.

---

## Step 2: Build the Unified Post Payload

All platforms are published in a **single API call** by listing them in the `posts` array.
This is the key advantage of the gateway — one request, many channels.

### Payload structure

```json
{
  "type": "now | schedule",
  "date": "2024-12-14T10:00:00.000Z",
  "shortLink": false,
  "tags": [],
  "posts": [
    {
      "integration": { "id": "<integration-id>" },
      "value": [
        {
          "content": "<platform-specific content>",
          "image": []
        }
      ],
      "settings": {
        "__type": "<provider-type>",
        // platform-specific settings (see Platform Settings below)
      }
    }
    // repeat for each platform
  ]
}
```

- `"type": "now"` — publish immediately
- `"type": "schedule"` — publish at the specified `date`
- Multiple posts in the array = publish to all those platforms in one request

---

## Step 3: POST to Create

```bash
curl -s -X POST "$POSTIZ_BASE_URL/posts" \
  -H "Authorization: $POSTIZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '<payload>'
```

Success response:
```json
{
  "id": "post-group-id",
  "posts": [
    { "id": "post-id-1", "state": "QUEUE", "integration": { "identifier": "linkedin" } },
    { "id": "post-id-2", "state": "QUEUE", "integration": { "identifier": "x" } }
  ]
}
```

Store the group `id` in `outputRef` on the list item.

---

## Platform Settings Reference

Each platform requires a `settings` object with `"__type"` matching the provider identifier.

### 🟦 Platforms with NO custom settings (just `__type`)
```json
{ "__type": "threads" }
{ "__type": "mastodon" }
{ "__type": "bluesky" }
{ "__type": "telegram" }
{ "__type": "nostr" }
{ "__type": "vk" }
{ "__type": "kick" }
```

### 🐦 X (Twitter)
```json
{
  "__type": "x",
  "who_can_reply_post": "everyone | subscribers | mentioned"
}
```
- Twitter threads: use multiple objects in the `value` array

### 💼 LinkedIn (personal)
```json
{
  "__type": "linkedin",
  "post_as_images_carousel": false
}
```

### 🏢 LinkedIn Page
```json
{
  "__type": "linkedin-page",
  "post_as_images_carousel": false
}
```

### 📘 Facebook
```json
{
  "__type": "facebook",
  "url": "https://optional-link.com"
}
```

### 📸 Instagram (Facebook-linked)
```json
{
  "__type": "instagram",
  "post_type": "post | reel | story",
  "collaborators": []
}
```

### 📸 Instagram Standalone
```json
{
  "__type": "instagram-standalone",
  "post_type": "post | reel | story",
  "collaborators": []
}
```

### 🎬 YouTube
```json
{
  "__type": "youtube",
  "title": "Video Title",
  "type": "video | short",
  "selfDeclaredMadeForKids": false,
  "thumbnail": { "id": "img-id", "path": "https://..." },
  "tags": ["tag1", "tag2"]
}
```

### 🎵 TikTok
```json
{
  "__type": "tiktok",
  "privacy_level": "PUBLIC_TO_EVERYONE | MUTUAL_FOLLOW_FRIENDS | SELF_ONLY",
  "duet": false,
  "stitch": false,
  "comment": true,
  "autoAddMusic": false,
  "brand_content_toggle": false,
  "brand_organic_toggle": false,
  "content_posting_method": "DIRECT_POST"
}
```

### 🤖 Reddit
```json
{
  "__type": "reddit",
  "subreddit": [
    {
      "value": "r/subredditname",
      "label": "r/subredditname",
      "title": "Post title (required for Reddit)",
      "type": "self | link",
      "flair": { "id": "flair-id", "text": "Flair Name" }
    }
  ]
}
```
Note: Reddit requires a `title` per subreddit. Always generate a title from the item name.

### 📌 Pinterest
```json
{
  "__type": "pinterest",
  "board": "board-id",
  "title": "Pin Title",
  "link": "https://destination-url.com",
  "dominant_color": "#3b82f6"
}
```

### 🎨 Dribbble
```json
{
  "__type": "dribbble",
  "title": "Shot Title",
  "team": "team-id-or-null"
}
```

### 💬 Discord
```json
{
  "__type": "discord",
  "channel": "channel-id"
}
```

### 💬 Slack
```json
{
  "__type": "slack",
  "channel": "channel-name-or-id"
}
```

### ✍️ Medium
```json
{
  "__type": "medium",
  "title": "Article Title",
  "subtitle": "Optional subtitle",
  "canonical": "https://canonical-url.com",
  "publication": "publication-id-or-null",
  "tags": [
    { "value": "technology", "label": "Technology" }
  ]
}
```
Content: Pass full Markdown in the `content` field.

### 👨‍💻 Dev.to
```json
{
  "__type": "devto",
  "title": "Article Title",
  "main_image": "https://cover-image.com",
  "canonical": "https://canonical-url.com",
  "organization": "org-id-or-null",
  "tags": ["javascript", "webdev"]
}
```

### 🔷 Hashnode
```json
{
  "__type": "hashnode",
  "title": "Article Title",
  "subtitle": "Optional subtitle",
  "main_image": "https://cover-image.com",
  "publication": "publication-id",
  "tags": [{ "value": "tag-id", "label": "Tag Name" }]
}
```

### 📝 WordPress
```json
{
  "__type": "wordpress",
  "title": "Post Title",
  "main_image": { "id": "img-id", "path": "https://..." },
  "type": "post | page"
}
```

### 🏢 Google My Business
```json
{
  "__type": "gmb",
  "topicType": "STANDARD | EVENT | OFFER | ALERT",
  "callToActionType": "LEARN_MORE | SIGN_UP | SHOP | ORDER | GET_OFFER | BOOK | CALL",
  "callToActionUrl": "https://your-url.com"
}
```

### 📧 Listmonk (newsletter)
```json
{
  "__type": "listmonk",
  "subject": "Newsletter Subject",
  "preview": "Preview text shown in inbox",
  "list": ["list-id"],
  "template": "template-id"
}
```

### 🎓 Skool
```json
{
  "__type": "skool",
  "group": "group-id",
  "label": "General",
  "title": "Post Title"
}
```

### ⚡ Whop
```json
{
  "__type": "whop",
  "company": "company-id",
  "experience": "experience-id",
  "title": "Post Title"
}
```

---

## Find Optimal Posting Time

Before scheduling, check the best slot for a channel:

```bash
curl -s -H "Authorization: $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/integrations/<integration-id>/find-slot"
```

Returns the next optimal posting time. Use this as the `date` when `type: "schedule"`.

---

## Post Status Tracking

Check post status after publishing:

```bash
curl -s -H "Authorization: $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/posts?startDate=<ISO>&endDate=<ISO>"
```

States: `QUEUE | PUBLISHED | ERROR | DRAFT`

If any post returns `ERROR`, surface this to the user with the platform name.

---

## Content Formatting per Platform via Postiz

Even though Postiz is the gateway, Claude must still format content correctly per platform *before* passing it to the API. The `content` field is what actually gets posted.

| Platform | Content format | Character limit |
|---|---|---|
| X / Twitter | Plain text. Thread = multiple `value` objects | 280 per tweet |
| LinkedIn | Plain text with line breaks | 3,000 |
| Instagram | Caption + hashtags | 2,200 |
| Facebook | Plain text + optional link | 63,206 |
| Reddit | Markdown (for self posts) | No hard limit |
| Mastodon | Plain text + hashtags | 500 |
| Bluesky | Plain text + hashtags | 300 |
| Medium / Hashnode / Dev.to | Markdown | No hard limit |
| WordPress | Markdown or HTML | No hard limit |
| YouTube | Description (not the video itself) | 5,000 |
| Listmonk | HTML or Markdown newsletter body | No hard limit |

Always read `references/action-playbooks.md` for content generation rules per platform, then pass the formatted content through this gateway.

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| 401 Unauthorized | Invalid API key | Ask user to re-enter key |
| `disabled: true` on integration | Channel disconnected | Ask user to reconnect in Postiz |
| 429 Too Many Requests | Rate limit hit | Wait and retry; batch more posts per request |
| `state: ERROR` on post | Platform-side rejection | Check content length / format; retry |
| Missing `integration.id` | Channel not connected | Show available integrations, ask user to pick |
