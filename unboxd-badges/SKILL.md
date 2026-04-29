---
did: skill:029
version: "1.0.0"
created: "2026-04-29"
name: unboxd-badges
description: >
  Issues and verifies UnboxdBadges — verifiable credentials attesting a
  contributor's skills and SFIA proficiency level (1–7) based on demonstrated
  OSS activity. Abstraction layer: chain, DID, issuer model, and assessment
  framework are TBD and plug in without changing this interface. Use whenever
  a badge needs to be issued, verified, displayed, or queried — from any skill
  or directly by a user. Trigger on: "issue a badge", "verify a badge",
  "what badges do I have", "attest this contribution", "UnboxdBadge",
  "SFIA credential".
---

# UnboxdBadges

Verifiable credentials for OSS contributors.
Attests skills + SFIA proficiency level (1–7) based on demonstrated activity.

> **Frameworks — fetch before acting:**
> - Credential schema + stubs: https://github.com/opensaasapps/frameworks/tree/main/unboxd-badges-schema
> - SFIA levels + skill codes: https://github.com/opensaasapps/frameworks/tree/main/sfia

---

## Interface (stable — does not change when implementation plugs in)

### Issue
```json
{
  "action": "issue",
  "recipient": { "github_username": "...", "identity": "..." },
  "skill": "{skill_name}",
  "sfia_level": null,
  "evidence": { "type": "...", "url": "...", "description": "..." },
  "context": "..."
}
```
Returns: `badge_id`, `badge_url`, `readme_badge`, `status`, `issued_at`

### Verify
```json
{ "action": "verify", "badge_id": "..." }
```
Returns: `valid`, all credential fields, `chain_verified`, `issuer_trusted`

### Query
```json
{ "action": "query", "github_username": "..." }
```
Returns: array of badges for that contributor

---

## Behaviour

Fetch https://github.com/opensaasapps/frameworks/tree/main/unboxd-badges-schema
for field definitions, evidence types, status values, pending registry
location, and all [FUTURE PLUG-IN] stubs.

Map the activity to a SFIA skill code using:
https://github.com/opensaasapps/frameworks/tree/main/sfia

Pass `sfia_level: null` — level is assigned by the assessment framework
[FUTURE PLUG-IN].

Add the returned `readme_badge` to the fork README under the upstream
credit block.
