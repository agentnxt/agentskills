---
did: skill:021
version: "1.0.0"
created: "2026-04-29"
name: rebrand-value-index
description: >
  Scores any open-source software project on whether rebranding it is worth
  doing — and explains exactly why, with a plain-English verdict. Outputs:
  score, verdict (Recommended / Possible / Not Recommended / Strongly
  Discouraged), suggested deployment mode, what breaks, what survives. Use
  whenever a user wants to fork and rebrand an OSS project, evaluate white-
  labelling risk, or understand what rebranding breaks. Also called by other
  skills (e.g. coolify-one-click-deploy) as a pre-flight check. Trigger on:
  "should I rebrand X", "is it worth rebranding", "what breaks if I rename",
  "can I white-label X", "rebrand risk", "is X safe to fork and rebrand".
---

# Rebrand Value Index (RVI)

Scores an OSS project on rebrand value. Returns a structured verdict.
Callable standalone or as a sub-step by other skills.

> **Frameworks — fetch before scoring:**
> - Scoring signals + verdicts: https://github.com/opensaasapps/frameworks/tree/main/rebrand-scoring
> - Brand recognition registry: https://github.com/opensaasapps/frameworks/tree/main/known-brands

---

## Inputs

| Input | Source |
|---|---|
| GitHub repo URL | From user or calling skill |
| Intended use | Optional — sharpens the verdict |
| Target mode | Optional — `unboxd.cloud` or `opensaasapps` |

---

## Step 1 — Fetch repo signals

```
GET https://api.github.com/repos/{owner}/{repo}
  → stargazers_count, license.spdx_id, description, topics

GET https://api.github.com/repos/{owner}/{repo}/contents/
  → look for: TRADEMARK, NOTICE, BRANDING, FUNDING.yml, updater/

GET https://api.github.com/repos/{owner}/{repo}/contents/README.md
  → scan for: ecosystem, updater, EE, trademark signals

GET docker-compose.yml / docker-compose.yaml / compose.yml
  → scan for: updater services, non-upstream images
```

---

## Step 2 — Score

Fetch https://github.com/opensaasapps/frameworks/tree/main/rebrand-scoring
Apply every matching signal. Sum the points.

Check brand recognition against:
https://github.com/opensaasapps/frameworks/tree/main/known-brands

---

## Step 3 — Output

Apply verdict thresholds from the rebrand-scoring framework. Present:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REBRAND VALUE INDEX — {UPSTREAM_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Score:    {score}
  Verdict:  {emoji} {VERDICT}

  Scoring breakdown:
  [{points}]  {signal description}
  ...
  ─────────
  Total: {score}

  What breaks:   {breaks[] list}
  What survives: {survives[] list}

  Recommendation:
  {2–4 plain-English sentences. Direct. Name the better option.}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Return the full output contract defined in the rebrand-scoring framework.
