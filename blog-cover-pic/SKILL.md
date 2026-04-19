---
name: blog-cover-pic
description: Use this skill when the user asks to "generate a blog cover image", "create OG images", "make social sharing images", "generate a featured image", "create blog hero image", "generate Open Graph image", or "generate JSON-LD for a blog post". Produces publication-ready cover images and structured data for blog posts.
---

# Blog Cover Pic Creator

## Goal

Generate a complete set of blog post visual assets:

- **Feature image** (1200x630) — hero/cover image for the blog post itself
- **Open Graph image** (1200x630) — optimized for social sharing (Facebook, Twitter, LinkedIn)
- **Google image** (1200x630) — optimized for Google Discover thumbnails
- **JSON-LD** — Article structured data referencing all images

## Inputs

Collect these from the user before running:

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `title` | Yes | — | Blog post title |
| `subtitle` | No | — | Tagline or summary line |
| `author` | No | — | Author name |
| `slug` | Yes | — | URL slug, used for output filenames |
| `brand_color` | No | `#1a1a2e` | Primary brand color (hex) |
| `accent_color` | No | `#e94560` | Accent color (hex) |
| `logo_path` | No | — | Path to a logo PNG to overlay |
| `date` | No | today | Publish date (YYYY-MM-DD) |
| `image_base_url` | Yes (for JSON-LD) | — | Base URL where images will be hosted |
| `output_dir` | Yes | — | Where to write generated files |

### Font Configuration

Fonts can be specified **per element** and support three formats:

| Format | Example | Description |
|--------|---------|-------------|
| Local file | `/path/to/Font.ttf` | Any local .ttf or .otf file |
| Google Fonts | `google:Inter` | Auto-downloaded from Google Fonts (bold weight) |
| Google Fonts + weight | `google:Playfair Display:400` | Specific weight variant |

**Font arguments:**
- `--font-path` — default font for all text elements
- `--title-font` — font for title (overrides `--font-path`)
- `--subtitle-font` — font for subtitle (overrides `--font-path`)
- `--author-font` — font for author name (overrides `--font-path`)

**Font size arguments:**
- `--title-size` (default: 48), `--subtitle-size` (default: 26), `--author-size` (default: 20)
- `--og-title-size` (default: 56), `--google-title-size` (default: 64)

### Color Configuration

| Argument | Default | Description |
|----------|---------|-------------|
| `--title-color` | `#FFFFFF` | Title text color |
| `--subtitle-color` | lightened accent | Subtitle text color |
| `--author-color` | `#CCCCCC` | Author text color |
| `--brand-color` | `#1a1a2e` | Base background color |
| `--accent-color` | `#e94560` | Accent elements (bars, decorations) |

### Gradient Configuration

| Argument | Default | Description |
|----------|---------|-------------|
| `--gradient-start` | derived from brand-color | Start color of background gradient |
| `--gradient-end` | derived from brand-color | End color of background gradient |
| `--gradient-direction` | `vertical` | One of: `vertical`, `horizontal`, `diagonal-down`, `diagonal-up` |

### Font Awesome Icons

Add a decorative Font Awesome (free/open-source) icon to the feature image:

| Argument | Default | Description |
|----------|---------|-------------|
| `--icon` | none | Icon name: `code`, `rocket`, `globe`, `star`, `github`, etc. |
| `--icon-style` | `solid` | Style: `solid`, `regular`, or `brands` (for github/twitter/etc) |
| `--icon-color` | lightened accent | Icon color (hex) |

Common icons: `star`, `heart`, `code`, `rocket`, `globe`, `bolt`, `lightbulb`, `book`, `newspaper`, `robot`, `database`, `server`, `cloud`, `terminal`, `bug`, `trophy`. Brand icons (use `--icon-style brands`): `github`, `twitter`, `linkedin`, `docker`, `python`, `react`, `node`.

## Workflow

### Step 1: Bootstrap environment

```bash
bash {baseDir}/scripts/bootstrap.sh
```

Creates a Python venv at `{baseDir}/.venv/` and installs Pillow. Idempotent.

### Step 2: Generate images

**Basic usage:**

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/generate_cover.py \
  --title "Your Blog Title" \
  --subtitle "Optional subtitle" \
  --author "Author Name" \
  --slug "your-blog-title" \
  --output-dir ./output
```

**With custom fonts (Google Fonts):**

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/generate_cover.py \
  --title "Your Blog Title" \
  --slug "your-blog-title" \
  --title-font "google:Inter" \
  --subtitle-font "google:Lora" \
  --author-font "google:Source Sans Pro:400" \
  --output-dir ./output
```

**With full customization:**

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/generate_cover.py \
  --title "Your Blog Title" \
  --subtitle "A deep dive" \
  --author "Jane Doe" \
  --slug "your-blog-title" \
  --title-font "google:Playfair Display" \
  --subtitle-font "google:Inter:400" \
  --title-color "#FFFFFF" \
  --subtitle-color "#FFD700" \
  --author-color "#AAAAAA" \
  --brand-color "#0d1117" \
  --accent-color "#58a6ff" \
  --gradient-start "#0d1117" \
  --gradient-end "#161b22" \
  --gradient-direction diagonal-down \
  --icon code \
  --icon-color "#58a6ff" \
  --logo path/to/logo.png \
  --output-dir ./output
```

### Step 3: Generate JSON-LD

```bash
{baseDir}/.venv/bin/python {baseDir}/scripts/generate_jsonld.py \
  --title "Your Blog Title" \
  --author "Author Name" \
  --date "2026-03-19" \
  --slug "your-blog-title" \
  --description "A brief description of the post" \
  --image-base-url "https://example.com/images" \
  --publisher-name "Your Brand" \
  --output-dir ./output
```

### Step 4: Verify outputs

```bash
# Check image dimensions
{baseDir}/.venv/bin/python -c "
from PIL import Image
for suffix in ['feature', 'og', 'google']:
    img = Image.open('output/your-blog-title-' + suffix + '.png')
    assert img.size == (1200, 630), f'{suffix}: unexpected size {img.size}'
    print(f'{suffix}: {img.size} OK')
"

# Validate JSON-LD
python3 -c "
import json
d = json.load(open('output/your-blog-title-jsonld.json'))
assert d['@type'] == 'Article'
assert len(d['image']) == 3
print('JSON-LD valid')
"
```

## Output Files

For slug `my-post`, the output directory will contain:

- `my-post-feature.png` — Full design: title + subtitle + author + decorative branding + optional icon
- `my-post-og.png` — Simplified: large title + brand mark, dark overlay for contrast
- `my-post-google.png` — Maximum contrast: very large title only, no decorations
- `my-post-jsonld.json` — Article schema with image array

## Image Variant Differences

| Variant | Text | Decorations | Use Case |
|---------|------|-------------|----------|
| Feature | Title + subtitle + author | Full (stripes, circles, dots, vignette, icon) | Blog hero image |
| OG | Title only (large) | Minimal (dark overlay, accent bar) | Social media thumbnails |
| Google | Title only (very large) | None (accent lines only) | Google Discover small thumbnails |

## HTML Integration

After generating, add these tags to your blog post `<head>`:

```html
<!-- Open Graph -->
<meta property="og:image" content="https://example.com/images/my-post-og.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:title" content="Your Blog Title" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://example.com/images/my-post-og.png" />

<!-- Google Discover -->
<meta name="robots" content="max-image-preview:large" />

<!-- JSON-LD (paste contents of the generated file) -->
<script type="application/ld+json">
  { ... }
</script>
```

## Requirements

- Python 3.9+
- Internet connection for first bootstrap (pip install Pillow) and Google Fonts / Font Awesome download
- Downloaded fonts are cached in `{baseDir}/.font-cache/` for subsequent runs
