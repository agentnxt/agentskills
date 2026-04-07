# Backends Reference

How to read lists from and write status back to each supported persistence backend.

---

## Backend: Notion Database

### Reading the list

Use the Notion MCP to fetch all pages from the database:

```
Tool: notion-fetch
Input: { "url": "<database_url>" }
```

Or search within the workspace:
```
Tool: notion-search
Input: { "query": "", "filter": { "property": "object", "value": "page" } }
```

The database must have at minimum:
- A `Name` / `Title` property (text)
- A `Status` property (select or status type) with values including `pending` / `in_progress` / `done`

Recommended additional properties:
```json
{
  "Name":         "title",
  "Status":       "select",       // pending | in_progress | done | skipped
  "Type":         "select",       // schema.org type (Product, Article, Person, etc.)
  "Description":  "rich_text",
  "URL":          "url",
  "Keywords":     "multi_select",
  "Platform":     "multi_select", // linkedin | twitter | blog | email | etc.
  "Action":       "select",       // research | write | email
  "ActionTaken":  "select",       // populated after completion
  "OutputRef":    "url",          // link to output (published post, doc, etc.)
  "CompletedAt":  "date",
  "Notes":        "rich_text"
}
```

### Filtering pending items

After fetching, filter pages where `Status` property = `pending` (case-insensitive). Pick the first result.

### Updating status

```
Tool: notion-update-page
Input: {
  "page_id": "<page_id>",
  "properties": {
    "Status": { "select": { "name": "in_progress" } }
  }
}
```

After completion:
```
Tool: notion-update-page
Input: {
  "page_id": "<page_id>",
  "properties": {
    "Status":      { "select": { "name": "done" } },
    "ActionTaken": { "select": { "name": "<action_label>" } },
    "CompletedAt": { "date": { "start": "<ISO 8601 datetime>" } },
    "OutputRef":   { "url": "<output_url_if_any>" }
  }
}
```

---

## Backend: JSON File

### File schema

The list is stored as a JSON array of items. Each item follows this structure:

```json
{
  "id": "unique-string-or-number",
  "name": "Item Name",
  "type": "Product",
  "status": "pending",
  "description": "Optional description",
  "url": "https://...",
  "keywords": ["keyword1", "keyword2"],
  "platform": ["linkedin", "twitter"],
  "action": "write",
  "metadata": {
    // schema.org type-specific fields go here
    // see schema-types.md for field lists per type
  },
  "actionTaken": null,
  "outputRef": null,
  "completedAt": null,
  "notes": ""
}
```

### Reading the list

```bash
cat /path/to/list.json
```

Parse the JSON array. Filter items where `"status": "pending"`. Pick index 0.

### Updating status

Read the full file, mutate the target item, write back:

```bash
# Example using Python inline
python3 -c "
import json, sys
with open('/path/to/list.json') as f:
    data = json.load(f)
for item in data:
    if item['id'] == 'TARGET_ID':
        item['status'] = 'in_progress'
        break
with open('/path/to/list.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

After completion, update `status`, `actionTaken`, `completedAt`, `outputRef` in the same way.

---

## Backend: Inline / Pasted List

When the user pastes a list directly in chat:

- Accept any tabular format: Markdown table, CSV, numbered list, JSON array
- Parse into the canonical item schema (see JSON schema above)
- Hold state in the conversation context
- After processing, offer to export the updated list as:
  - A JSON file (save to `/mnt/user-data/outputs/list.json`)
  - A Notion DB (create pages via `notion-create-pages`)
- **Remind the user** that this list will not persist between conversations unless exported

---

## Status Values (Canonical)

| Value | Meaning |
|---|---|
| `pending` | Not yet processed |
| `in_progress` | Currently being worked on |
| `done` | Action completed successfully |
| `skipped` | Intentionally skipped by user |
| `error` | Action failed, needs retry |

Map platform-specific synonyms: `todo` → `pending`, `not started` → `pending`, `complete` → `done`.
