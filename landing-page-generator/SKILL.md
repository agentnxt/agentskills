---
name: landing-page-generator
description: Generates a polished, production-grade landing page by scraping and referencing content from an existing website. Use this skill whenever a user wants to create a landing page inspired by or based on an existing site — even if they phrase it as "build a landing page from this URL", "make a landing page like my current site", "redesign my homepage", "convert my site into a landing page", "create a landing page based on this website", or "use my site content for a new landing page". Trigger this skill when a URL or uploaded site file is provided alongside any intent to produce a landing page. Always use this skill even if the user only provides a URL with a vague request — infer landing page intent and proceed.
---

# Landing Page Generator

Generate a beautiful, production-grade landing page by extracting content from an existing website (via URL or uploaded file) and redesigning it with high visual quality.

---

## Step 1: Gather the Source

**If the user provides a URL:**
- Use `web_fetch` to retrieve the page content
- Extract: headline/tagline, subheadings, feature descriptions, CTA text, testimonials, pricing info, brand name, color hints, and any other meaningful copy

**If the user uploads a file (HTML, PDF, screenshot, etc.):**
- Read the file from `/mnt/user-data/uploads/`
- Extract the same content as above

If neither is provided yet, ask the user:
> "Please share the URL of your existing site, or upload the file you'd like me to reference."

---

## Step 2: Clarify Output Format

If the user hasn't specified an output format, ask:
> "Would you like the landing page as a **single HTML file** (with CSS & JS inline, easy to open in any browser) or a **React component** (.jsx)?"

Default to HTML if the user seems non-technical or doesn't respond.

---

## Step 3: Design the Landing Page

Before writing any code, commit to a bold aesthetic direction based on the source site's tone and content. Reference the frontend-design skill principles:

- **Tone**: Infer from the source content (e.g., SaaS → clean & modern; creative portfolio → expressive & bold; e-commerce → energetic & conversion-focused)
- **Typography**: Choose distinctive, characterful font pairings — avoid Inter, Roboto, Arial
- **Color**: Extract brand colors from the source if available; otherwise derive a cohesive palette
- **Layout**: Use asymmetry, generous spacing, visual hierarchy — avoid cookie-cutter templates
- **Motion**: Add subtle CSS animations (fade-ins, scroll reveals, hover states)
- **Differentiation**: One memorable visual element — a bold hero, an animated gradient, a unique section divider

**Never produce generic AI-looking pages.** Each output should feel genuinely designed.

---

## Step 4: Build the Landing Page

### Recommended Sections (adapt based on source content):

1. **Hero** — Strong headline, subheadline, primary CTA button
2. **Features / Benefits** — 3–6 key value props with icons or visuals
3. **Social Proof** — Testimonials, logos, stats (if found in source)
4. **How It Works** — Step-by-step if applicable
5. **Pricing** — If pricing info exists in the source
6. **Final CTA** — Closing pitch + button
7. **Footer** — Brand name, links, copyright

### HTML Output Guidelines:
- Single self-contained `.html` file
- All CSS in a `<style>` block in `<head>`
- All JS in a `<script>` block before `</body>`
- Use Google Fonts via `<link>` for typography
- Responsive (mobile-first with media queries)
- Semantic HTML5 elements

### React Output Guidelines:
- Single `.jsx` file with default export
- Styled with Tailwind utility classes
- Use `lucide-react` for icons if needed
- No required props — fully self-contained with hardcoded content from source

---

## Step 5: Save and Present

Save the output to `/mnt/user-data/outputs/landing-page.[html|jsx]` and use `present_files` to share it with the user.

Then briefly note:
- The aesthetic direction chosen and why
- Any content that was inferred or filled in (e.g., placeholder CTAs)
- What the user might want to customize next

---

## Design Quality Checklist

Before finalizing, verify:
- [ ] Fonts are distinctive (not system fonts)
- [ ] Color palette is cohesive with clear dominant + accent colors
- [ ] Hero section has strong visual impact
- [ ] CTAs are prominent and action-oriented
- [ ] Layout has visual rhythm and hierarchy
- [ ] Animations are present but not distracting
- [ ] Mobile responsive
- [ ] No Lorem Ipsum — all copy comes from the source site
