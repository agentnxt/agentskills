# Skill Manifest

Every new registry skill should include a `skill.json` manifest at the root of its skill folder:

```text
skills/<skill-id>/skill.json
```

The manifest makes the skill registry searchable, validateable, and safer to consume programmatically.

Existing imported skill folders can be migrated gradually. Normal validation warns about missing manifests; strict validation enforces them.

## Required fields

| Field | Purpose |
| --- | --- |
| `schemaVersion` | Manifest schema version. Use `1.0.0`. |
| `id` | Stable lowercase registry id. Should match the skill folder name. |
| `name` | Human-readable skill name. |
| `version` | Skill package version. SemVer or date-based versions are accepted. |
| `description` | Short explanation of what the skill does. |
| `status` | One of `experimental`, `active`, `maintenance`, or `deprecated`. |
| `license` | License identifier or license note. |
| `entrypoints` | The `SKILL.md` path and optional docs/config paths. |
| `runtime` | Runtime type and supported platforms. |
| `permissions` | Network, filesystem, shell, browser, and secret requirements. |
| `maintainers` | At least one maintainer contact. |

## Example

```json
{
  "schemaVersion": "1.0.0",
  "id": "example-skill",
  "name": "Example Skill",
  "version": "0.1.0",
  "description": "A minimal example skill manifest for the AGenNext skill registry.",
  "status": "experimental",
  "homepage": "https://github.com/AGenNext/skill-registry/tree/main/skills/example-skill",
  "repository": "https://github.com/AGenNext/skill-registry",
  "license": "MIT",
  "tags": ["example", "starter"],
  "categories": ["documentation"],
  "entrypoints": {
    "skill": "SKILL.md",
    "readme": "README.md"
  },
  "runtime": {
    "type": "claude-skill",
    "packageManager": "none",
    "platforms": ["claude", "claude-code"]
  },
  "dependencies": [],
  "permissions": {
    "network": "none",
    "filesystem": "none",
    "shell": "none",
    "browser": "none",
    "secrets": [],
    "notes": "This example skill requires no external access."
  },
  "outputs": ["markdown"],
  "maintainers": [
    {
      "name": "AGenNext",
      "github": "AGenNext"
    }
  ],
  "security": {
    "reviewed": false,
    "reviewNotes": "Example manifest only."
  }
}
```

## Status values

- `experimental` - early or proof-of-concept skill; behavior may change.
- `active` - maintained and recommended for normal use.
- `maintenance` - receives fixes but no major feature work.
- `deprecated` - kept for compatibility or historical reference; users should migrate.

## Permission values

Use the least permissive accurate value.

### `network`

- `none` - does not require network access.
- `optional` - can use network access, but has offline or local-only behavior.
- `required` - cannot function without network access.

### `filesystem`

- `none` - does not read or write local files.
- `read` - reads local files or project context.
- `read-write` - writes files, edits projects, stores state, or creates artifacts.

### `shell`

- `none` - does not execute shell commands.
- `optional` - can execute commands for enhanced workflows.
- `required` - depends on shell execution.

### `browser`

- `none` - does not control or inspect a browser.
- `optional` - can use browser automation for optional workflows.
- `required` - depends on browser automation.

### `secrets`

List required environment variable names only. Never include secret values.

## Validation

The schema lives at:

```text
schemas/skill.schema.json
```

Run migration-friendly validation:

```bash
npm run validate:registry
```

Run strict validation:

```bash
npm run validate:registry -- --strict
```

## Best practices

- Keep `id` stable forever after publishing.
- Keep `SKILL.md` focused and executable by an assistant.
- Put long background material in separate docs and reference it from `SKILL.md`.
- Document dangerous capabilities in `permissions.notes`.
- Add `promptInjectionNotes` for skills that browse, ingest files, or trust external sources.
- Use `status: deprecated` before removing a skill.
