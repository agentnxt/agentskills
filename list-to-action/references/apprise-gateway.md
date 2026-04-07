# Apprise Notification Gateway

Apprise is the unified notification layer for all alerts and status updates.
One API call reaches 120+ notification services simultaneously.
Privacy-first, self-hostable, open-source.

**API Repo:** https://github.com/caronc/apprise-api
**Services list:** https://appriseit.com/services/
**Docs:** https://appriseit.com/getting-started/

---

## What Apprise Is (and How It Differs from Postiz)

| | Postiz | Apprise |
|---|---|---|
| Purpose | Social media publishing (scheduled content) | Push notifications (alerts, status, events) |
| Channels | 32 social/blog platforms | 120+ messaging/alert services |
| Use case | "Publish a post about this item" | "Notify me when this item is done / fails / needs attention" |
| Examples | LinkedIn, Twitter, WordPress | Telegram, Slack, Discord, PagerDuty, Pushover, email |

In list-to-action, Apprise fires notifications at key lifecycle moments:
- Item picked up (status: pending --> in_progress)
- Action completed successfully (status: done)
- Action failed or errored (status: error)
- Batch complete (all items processed)
- Custom triggers (user-defined, e.g. "notify me when blog is published")

---

## Setup Requirements

```
APPRISE_BASE_URL=http://your-apprise-instance:8000   # self-hosted
# OR use a public/shared instance
# No auth required by default; add HTTP Basic Auth if configured
```

### Quick Docker deploy (self-hosted)
```bash
docker run --name apprise \
  -p 8000:8000 \
  -v ./config:/config \
  -e APPRISE_STATEFUL_MODE=simple \
  -e APPRISE_WORKER_COUNT=1 \
  -e APPRISE_ADMIN=y \
  -d caronc/apprise:latest
```

### Health check
```bash
curl -s "$APPRISE_BASE_URL/status"
# Returns: OK (200) or error details (417)

# JSON response:
curl -s -H "Accept: application/json" "$APPRISE_BASE_URL/status"
```

---

## Two Operating Modes

### Mode 1: Stateless (fire-and-forget)
Pass Apprise service URLs directly in the request. No config stored.
Best for: one-off notifications, dynamic targets, simple integrations.

### Mode 2: Stateful (key-based)
Pre-save service URLs under a {KEY}. Trigger by key + optional tag.
Best for: persistent routing, team channels, tag-based routing (devops, personal, admin).

**Recommendation for list-to-action:**
- Use **stateful** mode with a key per context (e.g. `list-to-action`)
- Assign tags to group notification targets: `personal`, `ops`, `content`, `error`
- Claude fires: `POST /notify/list-to-action?tag=<context>`

---

## Core API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/status` | Health check |
| POST | `/notify/` | Stateless: send to URLs in payload |
| POST | `/notify/{KEY}` | Stateful: send to pre-saved URLs for KEY |
| POST | `/add/{KEY}` | Save Apprise URLs to persistent store |
| POST | `/del/{KEY}` | Delete config for KEY |
| GET | `/get/{KEY}` | Retrieve saved config for KEY |
| GET | `/json/urls/{KEY}` | List URLs and tags for KEY as JSON |

---

## Stateless Notification (simple, no setup needed)

Send to any Apprise URL directly — no prior configuration required:

```bash
# Minimal: form-encoded
curl -s -X POST \
  -d "urls=tgram://bottoken/chatid" \
  -d "body=Item processed: <item_name>" \
  "$APPRISE_BASE_URL/notify"

# With title and type
curl -s -X POST \
  -d "urls=slack://tokenA/tokenB/tokenC" \
  -d "title=List-to-Action" \
  -d "body=Done: <item_name> published to LinkedIn" \
  -d "type=success" \
  "$APPRISE_BASE_URL/notify"

# JSON payload
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "discord://webhookid/webhooktoken",
    "title": "Action Complete",
    "body": "Published: <item_name>",
    "type": "success",
    "format": "markdown"
  }' \
  "$APPRISE_BASE_URL/notify"

# Multiple services in one call
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "tgram://bottoken/chatid, slack://tokenA/tokenB/tokenC",
    "body": "Batch complete: 5 items processed",
    "type": "success"
  }' \
  "$APPRISE_BASE_URL/notify"
```

### Notification types
| type | When to use |
|---|---|
| `info` | Default. Item picked up, status updates |
| `success` | Action completed successfully |
| `warning` | Partial success, skipped items |
| `failure` | Action failed, error state |

### Body formats
| format | Use for |
|---|---|
| `text` | Default. Plain text |
| `markdown` | Rich formatting (bold, links, code) |
| `html` | HTML-capable services (email, Slack) |

---

## Stateful Notification (recommended for ongoing use)

### Step 1: Save your notification config once

```bash
# Save Telegram + Slack + Discord under key "list-to-action"
# with tags for routing
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "config": "# Apprise YAML Config\nversion: 1\nurls:\n  - tgram://bottoken/chatid:\n    - tag: personal\n    - tag: all\n  - slack://tokenA/tokenB/tokenC:\n    - tag: ops\n    - tag: all\n  - discord://webhookid/webhooktoken:\n    - tag: content\n    - tag: all\n  - mailto://user:pass@gmail.com:\n    - tag: error\n    - tag: all",
    "format": "yaml"
  }' \
  "$APPRISE_BASE_URL/add/list-to-action"
```

Or save as TEXT format (simpler):
```bash
curl -s -X POST \
  -d "urls=tgram://bottoken/chatid slack://tokenA/tokenB/tokenC" \
  "$APPRISE_BASE_URL/add/list-to-action"
```

### Step 2: Fire notifications by key (and optionally tag)

```bash
# Notify ALL services under key
curl -s -X POST \
  -d "body=Done: <item_name> published" \
  -d "type=success" \
  "$APPRISE_BASE_URL/notify/list-to-action"

# Notify only 'personal' tagged services
curl -s -X POST \
  -d "tag=personal" \
  -d "body=Your item is ready: <item_name>" \
  -d "type=success" \
  "$APPRISE_BASE_URL/notify/list-to-action"

# Notify 'error' tagged services on failure
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "error",
    "title": "Action Failed",
    "body": "Error processing: <item_name>\nAction: <action>\nReason: <error_msg>",
    "type": "failure"
  }' \
  "$APPRISE_BASE_URL/notify/list-to-action"
```

### Tag logic (AND / OR)
| Expression | Meaning |
|---|---|
| `"tag": "devops"` | All services tagged `devops` |
| `"tag": "dev, qa"` | Services tagged `dev` OR `qa` |
| `"tag": "leaders teamA"` | Services tagged `leaders` AND `teamA` |
| `"tag": "leaders teamA, leaders teamB"` | (`leaders` AND `teamA`) OR (`leaders` AND `teamB`) |

---

## Notification Triggers in list-to-action

Claude should fire Apprise notifications at these lifecycle events:

| Event | type | tag | Title | Body |
|---|---|---|---|---|
| Item picked up | `info` | `personal` | "Working on it" | "Starting: {item_name} ({action})" |
| Research complete | `success` | `content` | "Research Ready" | "Brief saved: {item_name}" |
| Post published | `success` | `content` | "Published" | "{item_name} posted to {platforms}" |
| Email sent | `success` | `personal` | "Email Sent" | "Sent: {subject} to {recipient}" |
| Item failed | `failure` | `error` | "Action Failed" | "{item_name}: {error_msg}" |
| Item skipped | `warning` | `personal` | "Skipped" | "{item_name} skipped — missing: {field}" |
| Batch complete | `success` | `all` | "Batch Done" | "{n} items processed. {success} ok, {failed} failed." |

### Sending a notification (Claude's routine)

```bash
# Generic helper pattern — adapt body/type/tag per event
notify() {
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"$1\",
      \"body\": \"$2\",
      \"type\": \"$3\",
      \"tag\": \"$4\",
      \"format\": \"markdown\"
    }" \
    "$APPRISE_BASE_URL/notify/list-to-action" \
  | python3 -c "import sys; r=sys.stdin.read(); print('Notified' if '200' in r or r.strip()=='' else 'Error: '+r)"
}

# Usage:
# notify "Published" "**Notion** published to LinkedIn, Twitter" "success" "content"
# notify "Error" "Failed: My Product\n**Reason:** API timeout" "failure" "error"
```

---

## Apprise URL Schemes (120+ services)

A curated selection of commonly used services. Full list at https://appriseit.com/services/

### Messaging / Chat
| Service | URL scheme |
|---|---|
| Telegram | `tgram://bottoken/chatid` |
| Slack | `slack://tokenA/tokenB/tokenC` OR `slack://webhook/` |
| Discord | `discord://webhookid/webhooktoken` |
| Microsoft Teams | `msteams://tokenA/tokenB/tokenC/tokenD` |
| WhatsApp (via Twilio) | `twilio://acctSID:authToken@FromNum/ToNum` |
| Signal (via Callmebot) | not natively supported; use webhook |
| Mattermost | `mmost://hostname/token` |
| Rocket.Chat | `rocket://user:pass@hostname/channel` |
| Matrix | `matrix://user:pass@hostname/#room` |
| XMPP | `xmpp://user:pass@hostname/recipient` |
| IRC | `irc://irc.server.net/#channel` |
| Zulip | `zulip://botEmailAddr/botKey/stream` |
| Google Chat | `gchat://workspace/key/token` |

### Push Notifications
| Service | URL scheme |
|---|---|
| Pushover | `pover://userKey/apiToken` |
| Pushbullet | `pbul://accessToken` |
| Ntfy.sh | `ntfy://topic` OR `ntfy://hostname/topic` |
| Gotify | `gotify://hostname/token` |
| Home Assistant | `hassio://hostname/accessToken` |
| Bark (iOS) | `bark://deviceKey/` |
| Pushplus | `pushplus://token` |
| Pushed | `pushed://appKey/appSecret` |

### Email
| Service | URL scheme |
|---|---|
| Gmail | `mailto://user:pass@gmail.com` |
| Generic SMTP | `mailto://user:pass@smtp.server.com:587` |
| Mailgun | `mailgun://user@domain/apiKey` |
| SendGrid | `sendgrid://apiKey/fromEmail` |
| Brevo | `brevo://apiKey/fromEmail` |
| Office365 | `o365://tenantId:accountEmail/clientId/clientSecret/toEmail` |

### DevOps / Alerts
| Service | URL scheme |
|---|---|
| PagerDuty | `pagerduty://integrationKey@hostname` |
| OpsGenie | `opsgenie://apiKey` |
| AWS SNS | `sns://accessKeyID/secretAccessKey/region/topic` |
| Grafana | `grafana://hostname/token` |
| Alertmanager | (webhook) |
| Nextcloud | `ncloud://user:pass@hostname/recipient` |

### Other
| Service | URL scheme |
|---|---|
| JSON (generic webhook) | `json://hostname/path` |
| Form (generic webhook) | `form://hostname/path` |
| MQTT | `mqtt://user:pass@hostname/topic` |
| RSS (Nextcloud News) | via Nextcloud |

---

## Attaching Files to Notifications

Apprise supports sending file attachments (e.g. the research brief, blog draft) with notifications:

```bash
# Attach a local file
curl -s -X POST \
  -F "body=Research brief attached" \
  -F "type=success" \
  -F "tag=content" \
  -F "attach=@/mnt/user-data/outputs/item-research.md" \
  "$APPRISE_BASE_URL/notify/list-to-action"

# Attach a remote URL (Apprise downloads and forwards)
curl -s -X POST \
  -F "body=Blog draft ready for review" \
  -F "attach=https://yourcdn.com/drafts/item-blog.md" \
  "$APPRISE_BASE_URL/notify/list-to-action"
```

Max attachment size: 200MB by default (configurable).

---

## Viewing Saved Config

```bash
# List all URLs and tags saved under a key
curl -s "$APPRISE_BASE_URL/json/urls/list-to-action" | python3 -m json.tool

# Response shape:
# {
#   "tags": ["personal", "ops", "content", "error", "all"],
#   "urls": [
#     { "url": "tgram://...", "tags": ["personal", "all"] },
#     { "url": "slack://...", "tags": ["ops", "all"] }
#   ]
# }
```

---

## Error Handling

| HTTP Code | Meaning | Action |
|---|---|---|
| 200 | All notifications sent | Log success |
| 204 | No config found for KEY | Remind user to run `/add/{KEY}` setup |
| 400 | Bad request (missing body, bad format) | Check payload shape |
| 424 | At least one notification failed | Log partial failure; check which service |
| 500 | Server error (disk/permission issue) | Check Apprise container logs |

On non-200 response, log the error and continue processing the list item.
Notification failures should never block the main action (publish/research/email).

---

## Setup Wizard (first run)

If Apprise is not yet configured, Claude should walk the user through setup:

1. **Check if Apprise is reachable:**
   ```bash
   curl -s "$APPRISE_BASE_URL/status"
   ```

2. **If not running, show Docker quickstart** (from Setup Requirements above)

3. **Ask user for their notification targets:**
   - "Where should I send notifications? (Telegram, Slack, Discord, email, etc.)"
   - Look up the URL scheme from the table above

4. **Save their config under key `list-to-action`:**
   ```bash
   curl -s -X POST \
     -d "urls=<their-apprise-urls>" \
     "$APPRISE_BASE_URL/add/list-to-action"
   ```

5. **Send a test notification:**
   ```bash
   curl -s -X POST \
     -d "body=Apprise gateway is working! list-to-action is ready." \
     -d "type=success" \
     "$APPRISE_BASE_URL/notify/list-to-action"
   ```

6. Confirm the user received it. If not, help debug the URL scheme.
