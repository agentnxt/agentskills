# Open Graph & Social Image Specifications

## Open Graph (Facebook, LinkedIn)

**Required tags:**
- `og:title` — post title
- `og:type` — `article`
- `og:image` — absolute URL to image
- `og:url` — canonical page URL

**Recommended image specs:**
- Dimensions: **1200x630px** (1.91:1 ratio)
- Format: PNG or JPEG
- File size: under 5MB
- Minimum: 600x315px (smaller will not render)

## Twitter Card

**Tags:**
- `twitter:card` — `summary_large_image`
- `twitter:image` — absolute URL to image
- `twitter:title` — post title
- `twitter:description` — post summary

**Image specs:**
- Dimensions: 1200x630px (same as OG)
- Minimum: 300x157px
- Maximum file size: 5MB
- Formats: PNG, JPEG, GIF, WEBP

## Google Discover

**Requirements:**
- Width: minimum **1200px**
- Use `max-image-preview:large` robots meta tag
- Avoid using site logo as the image
- High-quality, relevant to content
- Text in images should be minimal and readable at small sizes

**Meta tag:**
```html
<meta name="robots" content="max-image-preview:large" />
```

## Validation Tools

- **Facebook Sharing Debugger:** developers.facebook.com/tools/debug/
- **Twitter Card Validator:** cards-dev.twitter.com/validator
- **LinkedIn Post Inspector:** linkedin.com/post-inspector/
- **Google Rich Results Test:** search.google.com/test/rich-results
- **Schema.org Validator:** validator.schema.org
