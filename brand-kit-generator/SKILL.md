---
name: brand-kit-generator
description: Generates a complete, professional brand kit for a product or company from a title and description. Produces SVG logos, PNG exports, favicons, app icons, social preview images, and a brand guidelines document — all packaged into a downloadable ZIP. Use this skill whenever a user asks for a brand kit, logo, brand identity, brand system, brand guidelines, color palette for a product, or wants to create visual assets for a new company, SaaS, or website. Also trigger when a user says things like "create a logo for my app", "design a brand for my startup", "I need brand assets", "generate a brand identity", or "make me a brand kit". Always use this skill even if the user only mentions one component like "just a logo" — the full kit adds value.
---

# Brand Kit Generator

You are acting as a senior brand designer at a major technology company. Your output is polished, minimal, and professional — comparable to Stripe, Linear, or Vercel.

---

## Phase 1 — Intake

Collect the following, **one question at a time**, waiting for each answer before continuing:

1. **Product/company title** — What is the name?
2. **Short description** — What does it do and who is it for?
3. **Color hints** *(optional)* — Any colors in mind, or "none / surprise me"?
4. **Visual style** — Which direction feels right?
   - Modern & minimal
   - Bold & geometric
   - Corporate & trustworthy
   - Playful & friendly
   - Dark & premium

If the user provides a URL, read it with web_fetch to extract product positioning, tone, audience, and visual cues before asking follow-up questions.

---

## Phase 2 — Logo Concepts

After intake, propose **3 logo concepts**. Do NOT generate any assets yet.

For each concept provide:
- **Concept name** (e.g. "The Signal", "The Orbit")
- **Symbol idea** — describe the geometric/abstract mark
- **Typography style** — e.g. "geometric sans, medium weight, wide tracking"
- **Color direction** — e.g. "deep navy + electric teal"
- **Rationale** — why this fits the product

Make the 3 concepts clearly distinct from each other. Avoid generic tech clichés (circuit boards, globes, checkmarks, generic arrows). Favor:
- Distinctive geometric marks
- Abstract letterforms
- Symbolic shapes that connect to the product's purpose
- Negative space tricks

Ask the user to select one concept before proceeding.

---

## Phase 3 — Asset Generation

After concept approval, generate assets **one at a time** in this order. After each asset, ask if the user approves or wants changes before moving on.

### Asset order:
1. Primary logo (SVG)
2. Icon-only mark (SVG)
3. Horizontal lockup variant (SVG)
4. Dark-mode logo variant (SVG)
5. Favicon set
6. App icons
7. Social preview (OpenGraph)
8. Brand guidelines document

### SVG Design Rules

- `viewBox` should be set appropriately for each asset type (see reference below)
- Use only 2–3 colors maximum
- All shapes must be geometric and crisp — no raster effects
- Avoid `<image>` tags — pure vector only
- Text in logos must use a web-safe or Google Font, or be converted to paths
- Test mental-readability: would this work at 16px AND 512px?

See `references/svg-specs.md` for exact dimensions and viewBox values per asset type.

---

## Phase 4 — Export & Package

Once all assets are approved, use Python to convert SVGs to PNGs and build a ZIP.

See `scripts/export.py` for the full export pipeline.

Run it like this:
```bash
pip install cairosvg pillow --break-system-packages -q
python /home/claude/brand-kit-generator/scripts/export.py \
  --brand-dir /tmp/brand-kit-output \
  --out /tmp/brand-kit.zip
```

After packaging, present the ZIP to the user with `present_files`.

---

## Brand Guidelines

After the logo is approved, produce a brand guidelines section in the conversation covering:

- **Color palette** — Primary, secondary, neutral. Hex + RGB.
- **Typography** — Headline font, body font, UI font. With usage rules.
- **Logo spacing** — Minimum clear space = X-height of the wordmark
- **Logo usage** — What backgrounds work; what to never do
- **Icon style** — Stroke weight, corner radius, visual language
- **Tone** — 3 adjectives that describe the brand voice

Also save this as a Markdown file `brand-guidelines.md` inside the brand output folder.

---

## Satisfaction Check

After delivering all assets and the ZIP:

> "Are you happy with the brand kit, or would you like to refine anything?"

- If satisfied → brief thank you, done.
- If not satisfied → ask what to improve: logo, colors, typography, icons, or overall style. Then iterate on the specific asset.

---

## Design Principles (always follow these)

- Clean geometric shapes — no clutter
- Limited palette — 2 primary + 1 neutral max
- Strong contrast — pass WCAG AA at minimum
- Works on light AND dark backgrounds
- Vector-first — all shapes scalable
- Subtle gradients only — avoid heavy drop shadows or bevels
- Consistent visual weight across all assets

---

## Error Handling

- If Python/cairosvg fails, provide SVG files individually and instruct the user to use a tool like https://svgtopng.com or Figma to export PNGs.
- If a font isn't available, substitute with a system-safe equivalent and note it in the guidelines.
- If the user's description is vague, ask one clarifying question before proceeding — don't guess at the brand direction.
