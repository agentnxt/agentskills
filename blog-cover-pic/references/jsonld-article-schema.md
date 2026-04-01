# JSON-LD Article Schema Reference

## Schema.org Article Type

Full spec: schema.org/Article

## Required Properties (Google)

| Property | Type | Description |
|----------|------|-------------|
| `headline` | Text | Article title (max 110 chars recommended) |
| `image` | URL or ImageObject | One or more images. Google recommends an array. |
| `datePublished` | DateTime | ISO 8601 format (YYYY-MM-DD) |
| `author` | Person or Organization | Must include `name` |

## Recommended Properties

| Property | Type | Description |
|----------|------|-------------|
| `dateModified` | DateTime | Last modification date |
| `description` | Text | Short summary |
| `publisher` | Organization | Must include `name` and `logo` |
| `mainEntityOfPage` | WebPage | Canonical page URL |

## Image Best Practices

Google recommends providing multiple images in an array:

```json
"image": [
  "https://example.com/image-1200x630.png",
  "https://example.com/image-1200x900.png",
  "https://example.com/image-1200x1200.png"
]
```

- Minimum width: 696px
- Preferred: 1200px+
- Supported formats: JPEG, PNG, GIF, SVG, WebP

## Complete Example

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Building Reliable Distributed Systems",
  "description": "Lessons learned from running distributed systems in production.",
  "image": [
    "https://blog.example.com/images/reliable-systems-feature.png",
    "https://blog.example.com/images/reliable-systems-og.png",
    "https://blog.example.com/images/reliable-systems-google.png"
  ],
  "datePublished": "2026-03-19",
  "dateModified": "2026-03-19",
  "author": {
    "@type": "Person",
    "name": "Jane Doe"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Example Blog",
    "logo": {
      "@type": "ImageObject",
      "url": "https://blog.example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://blog.example.com/reliable-systems"
  }
}
```

## Embedding in HTML

```html
<script type="application/ld+json">
{ ... paste JSON-LD here ... }
</script>
```

Place in the `<head>` section of your HTML document.

## Testing

- **Google Rich Results Test:** search.google.com/test/rich-results
- **Schema.org Validator:** validator.schema.org
