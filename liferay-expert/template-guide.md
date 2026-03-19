# Liferay Theme Template System

## Overview

The templateized deployment lives at `/home/ubuntu/liferay-theme-template/` and provides one-click deployment of a branded Liferay portal.

## How It Works

```
.env (user edits) → generate-portal-ext.sh → runtime/portal-ext.properties + nginx.conf
                  → docker compose up      → setup container builds theme WAR from .env
                                           → deploys theme + applies via DB
                  → setup-pages.sh         → creates pages + adds widgets via API
```

## Template Variables

CSS and FTL templates use `{{VARIABLE}}` placeholders. The build scripts (`build-theme.sh` or `entrypoint-setup.sh`) substitute them from either `config/brand.conf` or Docker environment variables.

### Color System
All colors flow from 6 brand variables in `.env`:
- `COLOR_PRIMARY` → header bg, headings, dark buttons
- `COLOR_PRIMARY_LIGHT` → links, active states, primary buttons
- `COLOR_PRIMARY_LIGHTER` → hover highlights
- `COLOR_PRIMARY_LIGHTEST` → tinted backgrounds, info alerts
- `COLOR_SECONDARY` → footer bg
- `COLOR_ACCENT` → CTAs (defaults to PRIMARY_LIGHT)

### Layout Styles
`LAYOUT_STYLE` maps to `border-radius`:
- `sharp` → 0 (IBM Carbon / enterprise)
- `soft` → 4px (modern SaaS)
- `round` → 8px (friendly / consumer)

### Footer Configuration
Each `FOOTER_COL_N` is pipe-separated: `Heading|Link Text:URL|Link Text:URL|...`
Supports 1-6 columns. Grid auto-adjusts.

### Page Configuration
`SITE_PAGES` is comma-separated: `Name|/url|portlet-id`
The `setup-pages.sh` script creates each page and adds the specified widget.

## Two Deployment Modes

### Mode 1: Docker Compose (OOB for customers)
```bash
cp .env.example .env  # Edit
./scripts/generate-portal-ext.sh
docker compose up -d
# Wait, then:
./scripts/setup-pages.sh admin@email password
```

### Mode 2: Pre-built Docker Image (for selling)
```bash
# Build theme first
./scripts/build-theme.sh
# Build Docker image with theme baked in
docker build --build-arg THEME_ID=acmetheme -t mycompany/liferay-portal .
# Ship the image
docker push mycompany/liferay-portal
```

## Adding to the Template

### New CSS component
1. Add styles to `css/_custom.scss.tpl` using `{{VARIABLE}}` placeholders
2. Variables must exist in `.env.example` and be handled in build scripts

### New page type
1. Add to `SITE_PAGES` in `.env.example`
2. Use correct portlet ID (see api-reference.md)

### New footer column
1. Add `FOOTER_COL_N` in `.env.example`
2. Max 6 columns (CSS grid adjusts)

### New template variable
1. Add to `.env.example` with default
2. Add `{{VARIABLE}}` in templates
3. Add `-e "s|{{VARIABLE}}|${VARIABLE}|g"` in build scripts
