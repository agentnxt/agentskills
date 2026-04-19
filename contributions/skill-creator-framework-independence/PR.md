# PR: Add Framework Independence Principle to skill-creator

**Branch:** `feat/framework-independence-principle`
**Type:** RFC / Discussion — pure addition, no existing content modified

---

## Summary

Adds one new design principle — **Framework Independence** — to the Skill
Writing Guide in `skill-creator/SKILL.md`.

> *A skill must never own a framework. It may only reference one.*

---

## The core idea

Frameworks (scoring rubrics, taxonomies, standards like SFIA, API specs,
brand registries) should live in their own **public GitHub repositories**,
not embedded inside skill files.

Skills reference frameworks by **GitHub URL**:

```markdown
> **Framework:** https://github.com/opensaasapps/frameworks/tree/main/sfia
> Fetch this before proceeding. Do not copy its content into this skill.
```

Pinned to a version:
```markdown
> **Framework:** https://github.com/opensaasapps/frameworks/tree/v1.0/sfia
```

This means:
- Frameworks are versioned independently via Git tags
- Any skill, by anyone, can reference any public framework by URL
- Update the framework repo once → all skills that reference it benefit
- No skill "owns" a framework — the GitHub repo owner maintains it
- Works across any skills infrastructure — no dependency on directory layout

---

## What this adds to skill-creator

A single new section inserted between "Domain organization" and "Principle
of Lack of Surprise" in the Skill Writing Guide. Zero deletions. Zero
modifications to existing content.

Covers:
- The principle and its rules
- The GitHub URL reference pattern with version pinning examples
- A skill vs framework decision table
- Guidance to create a framework repo first, then reference it

---

## Why GitHub URLs specifically

We considered file path references but a GitHub URL is strictly better:

- The URL is the identity — no ambiguity, no directory convention to agree on
- Works across any skills infrastructure (Anthropic, third-party, private)
- Public frameworks are discoverable and community-contributable
- Version pinning via Git tags is universal and well-understood
- No new syntax to invent or standardise

---

## Origin

Emerged from building a skill suite in a single session (`agentnxxt/agentskills`).
Initially embedded SFIA levels, brand registries, and scoring rubrics inside
individual skills. When we caught the duplication across three skills, we
extracted them into a public `opensaasapps/frameworks` repo and had each
skill reference them by URL. The skills shrank, became easier to read, and
the frameworks became independently maintainable.

Example frameworks now living independently:
- https://github.com/opensaasapps/frameworks/tree/main/sfia
- https://github.com/opensaasapps/frameworks/tree/main/known-brands
- https://github.com/opensaasapps/frameworks/tree/main/rebrand-scoring
- https://github.com/opensaasapps/frameworks/tree/main/unboxd-badges-schema

---

## No open questions

The GitHub URL pattern requires no agreement on directory structure, loading
syntax, or runtime mechanisms. A skill fetches the URL, reads the content,
applies it. That's it.
