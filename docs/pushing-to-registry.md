# How to Push to the Skill Registry

This guide explains how to add or update a skill package in `AGenNext/skill-registry` and submit it for review.

## Overview

The registry stores skill packages primarily under the `skills/` directory. Each new skill should include a `SKILL.md` file for assistant-facing instructions and a `skill.json` manifest for machine-readable metadata.

Use this workflow when you want to:

- add a new skill to the registry
- update an existing registered skill
- publish a new version of a skill
- fix metadata, docs, examples, or packaging issues

## Prerequisites

Before pushing to the registry, make sure you have:

- access to the `AGenNext/skill-registry` GitHub repository
- Git installed locally
- a tested skill folder ready to add under `skills/`
- permission to publish any source code, prompts, examples, assets, or third-party materials included in the skill package

## Recommended skill folder layout

```text
skills/
└── your-skill-name/
    ├── SKILL.md
    ├── skill.json
    ├── README.md              # recommended
    ├── CHANGELOG.md           # recommended for versioned changes
    ├── docs/                  # optional
    ├── examples/              # optional
    └── assets/                # optional
```

At minimum, new skills should include `SKILL.md` and `skill.json`. Add `README.md` when setup or usage needs more detail.

## Skill documentation checklist

Each skill should answer these questions:

- What does the skill do?
- When should an assistant use it?
- What inputs does it expect?
- What outputs does it produce?
- What tools, APIs, databases, or services does it require?
- What environment variables or secrets are required?
- Does it read files, write files, run shell commands, browse, or call external services?
- What are its known limitations?
- How should users report issues or request improvements?

## Step 1: Clone the registry

```bash
git clone https://github.com/AGenNext/skill-registry.git
cd skill-registry
```

If you already have a local copy, update it first:

```bash
git checkout main
git pull origin main
```

## Step 2: Create a working branch

```bash
git checkout -b add-your-skill-name
```

Examples:

```bash
git checkout -b add-salesforce-gap-skill
git checkout -b update-feature-gap-analyzer
git checkout -b fix-skill-score-docs
```

## Step 3: Add or update the skill folder

For a new skill:

```bash
mkdir -p skills/your-skill-name
```

Copy your skill files into that folder.

Do not commit files such as:

```text
.env
.env.local
node_modules/
dist/
build/
coverage/
*.log
.DS_Store
```

If the skill is distributed as a packaged `.skill` file, keep the source files and metadata in the registry and document how the packaged artifact is generated.

## Step 4: Add `skill.json`

Create a manifest at:

```text
skills/your-skill-name/skill.json
```

See [`docs/skill-manifest.md`](skill-manifest.md) for the schema and examples.

## Step 5: Validate locally

Run registry validation:

```bash
npm run validate:registry
```

For strict validation across all skill folders:

```bash
npm run validate:registry -- --strict
```

If the skill has its own tests or build steps, run those too.

## Step 6: Rebuild the registry index

```bash
npm run build:index
```

This regenerates:

```text
registry.json
```

Commit `registry.json` with the skill changes.

## Step 7: Review the diff

```bash
git status
git diff
```

Confirm that the diff includes only intentional source, docs, metadata, and index changes.

## Step 8: Commit the change

```bash
git add skills/your-skill-name registry.json
git commit -m "registry: add your-skill-name"
```

For updates:

```bash
git commit -m "registry: update feature-gap-analyzer"
git commit -m "docs: improve skill-score setup guide"
```

## Step 9: Push and open a pull request

```bash
git push origin add-your-skill-name
```

Your PR description should include:

- skill name
- summary of what changed
- whether this is a new skill or an update
- validation commands you ran
- required secrets, APIs, databases, or services
- security notes for external content, files, shell commands, browser use, or network access
- examples or screenshots if useful

## Maintainer direct-push workflow

Maintainers with write access may push directly to `main` for small documentation or metadata fixes.

Use pull requests for new skills, large updates, security-sensitive changes, or changes that affect runtime behavior.

## Security checklist

Before pushing, confirm that:

- no API keys, tokens, cookies, private keys, or credentials are committed
- `.env` files are excluded or replaced with `.env.example`
- network, filesystem, shell, and browser access are disclosed in `skill.json`
- prompt-injection risks are documented when the skill ingests external content
- third-party assets and dependencies are allowed to be redistributed
- generated files and local caches are excluded unless intentionally published

Search for accidental secrets:

```bash
grep -R "API_KEY\|SECRET\|TOKEN\|PASSWORD\|PRIVATE KEY" skills/your-skill-name || true
```

## Troubleshooting

### Push rejected because branch is behind

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

### Wrong files were committed

```bash
git rm --cached path/to/file
git commit --amend
git push --force-with-lease
```

### Secret was committed

Rotate the secret immediately. Do not simply delete it in a later commit. Ask a maintainer to remove it from Git history if needed.

### Skill package is too large

Remove generated outputs, caches, dependency folders, large binaries, and packaged artifacts that can be rebuilt from source.

## Final pre-push checklist

- [ ] Skill lives under `skills/<skill-id>/`
- [ ] `SKILL.md` is present
- [ ] `skill.json` is present
- [ ] README is present when setup needs more detail
- [ ] Runtime and dependencies are documented
- [ ] Required environment variables are documented by name only
- [ ] Permissions are accurate
- [ ] Local validation passed
- [ ] `registry.json` was regenerated
- [ ] No secrets are included
- [ ] PR description includes validation and security notes
